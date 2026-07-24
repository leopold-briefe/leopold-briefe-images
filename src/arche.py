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
    g.add((subj, ACDH["hasLicense"], URIRef(license)))
    g.add((subj, ACDH["hasLicensor"], URIRef("https://id.acdh.oeaw.ac.at/none")))
    g.add((subj, ACDH["hasRightsHolder"], URIRef("https://id.acdh.oeaw.ac.at/none")))
    g.add((subj, ACDH["hasOwner"], URIRef("https://id.acdh.oeaw.ac.at/none")))
    g.add((subj, ACDH["hasNonLinkedIdentifier"], Literal(signatur)))

g.serialize(out_file)
