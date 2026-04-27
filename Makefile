.PHONY: install test docs serve clean

install:
	pip install -e ".[dev,docs]"

test:
	pytest

docs:
	cd docs && python -m quartodoc build && cd .. && quarto render docs

serve:
	quarto preview docs

clean:
	rm -rf dist build *.egg-info docs/_build docs/reference
