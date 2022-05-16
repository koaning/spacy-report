import subprocess
from pathlib import Path
from typer.testing import CliRunner

from spacy_report import __version__
from spacy_report.__main__ import report_cli

runner = CliRunner()


def test_version():
    """Confirm that we can get the version out."""
    result = runner.invoke(report_cli, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_smoke_test(tmpdir):
    """Merely a smoke test to make sure that 'it can run'."""
    result = runner.invoke(
        report_cli,
        [
            "textcat",
            "training/model-best/",
            "tests/data/train.spacy",
            "tests/data/train.spacy",
            str(tmpdir),
        ],
    )
    assert result.exit_code == 0

    # This model is taught to predict two classes.
    # We expect two charts, ie. two json files, per class.
    assert len(list(Path(tmpdir).glob("*.json"))) == 4


def test_spacy_detects_cli():
    """Make sure that we can call the commands directly from spaCy"""
    command = "python -m spacy report --help"
    response = subprocess.run(command.split(" "))
    assert response.returncode == 0
