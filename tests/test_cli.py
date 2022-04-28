from pathlib import Path
from typer.testing import CliRunner

from accuracy import __version__
from accuracy.__main__ import app

runner = CliRunner()


def test_version():
    """Confirm that we can get the version out."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_smoke_test(tmpdir):
    """Merely a smoke test to make sure that 'it can run'."""
    result = runner.invoke(
        app,
        [
            "report",
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
