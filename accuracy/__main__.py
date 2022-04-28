import spacy
import typer
import pathlib
import warnings
import altair as alt
from clumper import Clumper
from rich.progress import track
from rich.console import Console
from pkg_resources import resource_filename
from jinja2 import Environment, select_autoescape, FileSystemLoader

from accuracy._charts import make_plots
from accuracy import __version__

app = typer.Typer(
    name="accuraCy",
    add_completion=False,
    help="It's pronounced 'accura-see'. For spaCy models.",
)


@app.command()
def report(
    model_path: pathlib.Path = typer.Argument(None, help="Path to spaCy model"),
    train_path: pathlib.Path = typer.Argument(None, help="Path to training data"),
    dev_path: pathlib.Path = typer.Argument(None, help="Path to development data"),
    folder_out: pathlib.Path = typer.Argument(
        "reports", help="Output folder for reports"
    ),
    classes: str = typer.Option(None, help="Comma-separated string of classes to use"),
):
    """Generate a model report."""
    console = Console()
    console.print(f"Loading model at {model_path}")
    nlp = spacy.load(model_path)
    tags_of_interest = list(nlp("categories").cats.keys())
    if classes:
        for classname in classes.split(","):
            if classname not in tags_of_interest:
                console.print(
                    f"[red]Warning! '{classname}' label not found in model. Skipping... [/red]"
                )
        tags_of_interest = [c for c in tags_of_interest if c in classes.split(",")]
    clump_train = Clumper.read_jsonl(train_path)
    clump_dev = Clumper.read_jsonl(dev_path)

    # At the time of writing this the thinc library has an annoying
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        console.print("Running model on training data...")
        docs_train = list(nlp.pipe([_["text"] for _ in clump_train]))
        console.print("Running model on development data...")
        docs_dev = list(nlp.pipe([_["text"] for _ in clump_dev]))

    alt.data_transformers.disable_max_rows()

    if not folder_out.exists():
        folder_out.mkdir(parents=True)

    for tag in track(tags_of_interest, "Generating Charts"):
        p1, p2 = make_plots(clump_train, docs=docs_train, tag=tag)
        p3, p4 = make_plots(clump_dev, docs=docs_dev, tag=tag)
        json_hist = (
            p1.properties(title="Train") | p3.properties(title="Dev")
        ).to_json()
        pathlib.Path(f"reports/{tag}-hist.json").write_text(json_hist)
        json_scores = (
            p2.properties(title="Train") | p4.properties(title="Dev")
        ).to_json()
        pathlib.Path(f"reports/{tag}-scores.json").write_text(json_scores)

    env = Environment(
        loader=FileSystemLoader(resource_filename("accuracy", "templates")),
        autoescape=select_autoescape(["html", "xml"]),
    )

    dashboard = env.get_template("template.html").render(tags=tags_of_interest)
    pathlib.Path(folder_out, "index.html").write_text(dashboard)
    console.print("Done! You can view the report via;\n")
    console.print(f"python -m http.server --directory {folder_out} PORT \n")


@app.command()
def version():
    """Show version number."""
    return __version__


if __name__ == "__main__":
    app()
