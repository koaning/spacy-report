<img src="icon.png" width=175 height=175 align="right">

## accuraCy

> It's pronounced "accura-see". For spaCy models.

The goal of this project is to generate dashboards for spaCy models to help understand the accuracy metrics.

## usage

You'd typically run the command line interface via a command like:

```
python -m accuracy report training/model-best/ corpus/train.spacy corpus/dev.spacy
```

This will generate a folder, typically called "reports", that contains a full 
dashboard for the trained spaCy model found in `training/model-best`. The CLI
has a few configurable settings:

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
