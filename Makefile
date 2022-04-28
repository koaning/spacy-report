.PHONY: docs

black:
	black accuracy tests setup.py --check

install:
	python -m pip install --upgrade pip wheel twine
	python -m pip install -e ".[dev]"
	python tests/prepare.py en tests/data/train.jsonl tests/data/train.spacy "cat,dog"
	python -m spacy train tests/configs/config.cfg --output training/ --paths.train tests/data/train.spacy --paths.dev tests/data/train.spacy --nlp.lang en --gpu-id -1

flake:
	flake8 setup.py --count --statistics --max-complexity=10 --max-line-length=127
	flake8 accuracy --count --statistics --max-complexity=10 --max-line-length=127 --exclude __init__.py
	flake8 tests --count --statistics --max-complexity=10 --max-line-length=127 --exclude __init__.py

test:
	pytest tests

interrogate:
	interrogate -vv --ignore-nested-functions --ignore-semiprivate --ignore-private --ignore-magic --ignore-module --ignore-init-method --fail-under 100 tests
	interrogate -vv --ignore-nested-functions --ignore-semiprivate --ignore-private --ignore-magic --ignore-module --ignore-init-method --fail-under 100 accuracy

clean:
	rm -rf .ipynb_checkpoints
	rm -rf **/.ipynb_checkpoints
	rm -rf .pytest_cache
	rm -rf build
	rm -rf dist
	rm -rf accuraCy.egg-info

check: black flake interrogate test clean

pypi:
	python setup.py sdist
	python setup.py bdist_wheel --universal
	twine upload dist/*
