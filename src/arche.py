import json
import os
import shutil
import sys

import pandas as pd
import requests
from rdflib import RDF, Graph, Literal, Namespace, URIRef

from utils import make_title, signatur_and_license

TOP_COL = os.environ.get("TOPCOLID")
if TOP_COL:
    pass
else:
    print("TOPCOLID not set, abandone script")
    sys.exit()

LETTERS_SOURCE = "letters.json"
try:
    with open(LETTERS_SOURCE, "r", encoding="utf-8") as fp:
        metadata = json.load(fp)
except FileNotFoundError:
    print(f"{LETTERS_SOURCE} does not exist, need to download it first")
    metadata = requests.get(
        f"https://raw.githubusercontent.com/loepold-briefe/leopold-entities/refs/heads/main/json_dumps/{LETTERS_SOURCE}"
    ).json()

    with open(LETTERS_SOURCE, "w", encoding="utf-8") as fp:
        json.dump(metadata, fp, ensure_ascii=False)

lookup_dict = {}
for x in metadata.values():
    lookup_dict[x["lb_id"]] = x

to_ingest = "to_ingest"
out_file = os.path.join(to_ingest, "arche.ttl")
shutil.rmtree(to_ingest, ignore_errors=True)
os.makedirs(to_ingest, exist_ok=True)
g = Graph().parse("arche/arche_top_col.ttl")
ACDH = Namespace("https://vocabs.acdh.oeaw.ac.at/schema#")
TOP_COL_URI = URIRef(TOP_COL)
OOELA_URI = URIRef("https://id.acdh.oeaw.ac.at/leopold-briefe/facs/ooela")
NONE_URI = URIRef("https://id.acdh.oeaw.ac.at/none")


def add_shared_properties(graph: Graph, subject: URIRef, license_uri: str) -> None:
    graph.add((subject, ACDH["hasLicense"], URIRef(license_uri)))
    graph.add((subject, ACDH["hasLicensor"], NONE_URI))
    graph.add((subject, ACDH["hasRightsHolder"], NONE_URI))
    graph.add((subject, ACDH["hasOwner"], NONE_URI))
    graph.add(
        (subject, ACDH["hasDepositor"], URIRef("https://d-nb.info/gnd/132150654"))
    )
    graph.add(
        (subject, ACDH["hasDigitisingAgent"], URIRef("https://d-nb.info/gnd/132150654"))
    )
    graph.add(
        (
            subject,
            ACDH["hasMetadataCreator"],
            URIRef("https://id.acdh.oeaw.ac.at/pandorfer"),
        )
    )


with open("fc_reports/OÖLA/fileList.json", "r", encoding="utf-8") as fp:
    data = json.load(fp)

data = sorted(data, key=lambda x: x["filename"])

df = pd.DataFrame(data)
df.to_csv("tmp.csv", index=False)

for folder, ndf in df.groupby("directory"):
    # make collection md
    letter_id = os.path.split(folder)[-1]
    try:
        metadata = lookup_dict[letter_id]
    except KeyError:
        continue
    with open("tmp.json", "w", encoding="utf-8") as fp:
        json.dump(metadata, fp, ensure_ascii=False, indent=4)
    subj = URIRef(f"{TOP_COL}/{letter_id}")
    g.add((subj, RDF.type, ACDH["Collection"]))
    g.add((subj, ACDH["isPartOf"], OOELA_URI))
    title = make_title(metadata)
    g.add((subj, ACDH["hasTitle"], Literal(title, lang="de")))
    signatur, license = signatur_and_license(metadata)
    add_shared_properties(g, subj, license)
    g.add((subj, ACDH["hasNonLinkedIdentifier"], Literal(signatur)))
    g.add((subj, ACDH["hasExtent"], Literal(f"{len(ndf)} Seiten", lang="de")))
    g.add((subj, ACDH["hasTag"], Literal("IMAGE", lang="de")))
    previous_item = subj
    for i, (_, row) in enumerate(ndf.iterrows(), start=1):
        f_name = row["filename"]
        img_subj = URIRef(f"{TOP_COL_URI}/{f_name}")
        g.add((img_subj, RDF.type, ACDH["Resource"]))
        g.add((img_subj, ACDH["isPartOf"], subj))
        g.add((previous_item, ACDH["hasNextItem"], img_subj))
        facs_title = f"{title}, Seite {i}"
        g.add((img_subj, ACDH["hasTitle"], Literal(facs_title, lang="de")))
        g.add((img_subj, ACDH["hasCategory"], URIRef(row["hasCategory"])))
        g.add((img_subj, ACDH["hasNonLinkedIdentifier"], Literal(signatur)))
        add_shared_properties(g, img_subj, license)
        previous_item = img_subj

g.serialize(out_file)
