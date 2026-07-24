def make_title(metadata: dict) -> str:
    senders = ", ".join([x["value"] for x in metadata["sender"]])
    receivers = ", ".join([x["label"] for x in metadata["receiver"]])
    place_written = ", ".join([x["label"] for x in metadata["place_of_writing"]])
    title = f"{senders} an {receivers}, {metadata['written_date']}"
    if place_written:
        title = (
            f"{senders} an {receivers}, {metadata['written_date']} ({place_written})"
        )
    return title


def signatur_and_license(md: dict) -> str:
    archiv = md["archiv"][0]
    archiv_name = archiv["label"]
    license = archiv["has_license"]
    signatur = f"{archiv_name}, {md['collection']}, {md['signatur']}"

    return signatur, license
