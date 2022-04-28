<img src="icon.png" width=175 height=175 align="right">

## accuraCy

> It's pronounced "accura-see". For spaCy models.

The goal of this project is to generate reports for spaCy models.

## install 

You can install this project via pip. 

```
python -m pip install accuracy
```

Alternatively, you may also install the latest from git. 

```
python -m pip install "accuracy @ git+https://github.com/koaning/accuracy.git"
```

## usage
The `accuracy` project provides a command line interface that can
generate reports. The full CLI can also be explored via the `--help` flag. 

```
> python -m accuracy --help

Usage: python -m accuracy [OPTIONS] COMMAND [ARGS]...

  It's pronounced 'accura-see'. For spaCy models.

Options:
  --help  Show this message and exit.

Commands:
  report   Generate a model report.
  version  Show version number.
```

The most important command is the `report` command. You'd typically use it via 
a command similar to:

```
python -m accuracy report training/model-best/ corpus/train.spacy corpus/dev.spacy
```

This will generate a folder, typically called "reports", that contains a full 
dashboard for the trained spaCy model found in `training/model-best`. 

The CLI has a few configurable settings:

```text
Arguments:
  [MODEL_PATH]  Path to spaCy model
  [TRAIN_PATH]  Path to training data
  [DEV_PATH]    Path to development data
  [FOLDER_OUT]  Output folder for reports  [default: reports]

Options:
  --classes TEXT  Comma-separated string of classes to use
  --help          Show this message and exit.
```

