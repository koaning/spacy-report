import pathlib
import warnings
from pkg_resources import resource_filename

import spacy
from spacy.tokens import DocBin
import typer
import altair as alt
from rich.progress import track
from rich.console import Console
from jinja2 import Environment, select_autoescape, FileSystemLoader

from spacy_report._charts import make_plots
from spacy_report import __version__
from spacy.cli._util import app


report_cli = typer.Typer(
    name="report",
    add_completion=False,
    help="Generate reports for spaCy models.",
    no_args_is_help=True,
)
app.add_typer(report_cli)


@report_cli.command("version")
def version():
    """Print the version of spacy_report."""
    typer.echo(__version__)


@report_cli.command("textcat")
def textcat_report(
    model_path: pathlib.Path = typer.Argument(None, help="Path to spaCy model"),
    train_path: pathlib.Path = typer.Argument(None, help="Path to training data"),
    dev_path: pathlib.Path = typer.Argument(None, help="Path to development data"),
    folder_out: pathlib.Path = typer.Argument(
        "reports", help="Output folder for reports"
    ),
    classes: str = typer.Option(None, help="Comma-separated string of classes to use"),
):
    """Generate a report for textcat models."""
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

    orig_train_docbin = list(DocBin().from_disk(train_path).get_docs(nlp.vocab))
    orig_valid_docbin = list(DocBin().from_disk(dev_path).get_docs(nlp.vocab))

    # At the time of writing this the thinc library has an annoying warning
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        console.print("Running model on training data...")
        pred_train_clump = list(nlp.pipe([_.text for _ in orig_train_docbin]))
        console.print("Running model on development data...")
        pred_valid_clump = list(nlp.pipe([_.text for _ in orig_valid_docbin]))

        alt.data_transformers.disable_max_rows()

        if not folder_out.exists():
            folder_out.mkdir(parents=True)

        for tag in track(tags_of_interest, "Generating Charts"):
            # Prepare plotting objects
            p1, p2 = make_plots(orig_train_docbin, pred_train_clump, tag=tag)
            p3, p4 = make_plots(orig_valid_docbin, pred_valid_clump, tag=tag)

            # Render the density charts
            with alt.themes.enable("opaque"):
                json_hist = (
                    p1.properties(title="Train") | p3.properties(title="Dev")
                ).to_json()
            pathlib.Path(folder_out, f"{tag}-hist.json").write_text(json_hist)

            # Render the acc/precision/recall charts.
            with alt.themes.enable("opaque"):
                json_scores = (
                    p2.properties(title="Train") | p4.properties(title="Dev")
                ).to_json()
            pathlib.Path(folder_out, f"{tag}-scores.json").write_text(json_scores)

    env = Environment(
        loader=FileSystemLoader(resource_filename("spacy_report", "templates")),
        autoescape=select_autoescape(["html", "xml"]),
    )

    dashboard = env.get_template("template.html").render(tags=tags_of_interest)
    pathlib.Path(folder_out, "index.html").write_text(dashboard)
    console.print("Done! You can view the report via;\n")
    console.print(f"python -m http.server --directory {folder_out} PORT \n")


if __name__ == "__main__":
    app()
