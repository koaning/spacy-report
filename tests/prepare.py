"""Convert textcat annotation from JSONL to spaCy v3 .spacy format."""
import srsly
import typer
from pathlib import Path
from rich.progress import track

import spacy
from spacy.tokens import DocBin

def make_cats(json_labels, tags_of_interest):
    """Convert JSON labels to spaCy v3 cats."""
    labels = {k: 0.0 for k in tags_of_interest}
    for label in json_labels:
        if label in labels:
            labels[label] = 1.0
    return labels


def convert(lang: str, input_path: Path, output_path: Path, tags_of_interest:str):
    """Convert textcat annotation from JSONL to spaCy v3 .spacy format."""
    tags_of_interest = tags_of_interest.split(",")
    nlp = spacy.blank(lang)
    db = DocBin()
    for line in track(list(srsly.read_jsonl(input_path)), "Creating .spacy file."):
        doc = nlp.make_doc(line["text"])
        doc.cats = make_cats(line["cats"], tags_of_interest=tags_of_interest)
        db.add(doc)
    db.to_disk(output_path)


if __name__ == "__main__":
    typer.run(convert)
