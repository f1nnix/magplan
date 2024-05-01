SRC_DIR := src

.PHONY: lint isort black mypy

lint: isort black mypy

isort:
	isort $(SRC_DIR)

black:
	black --line-length 80 $(SRC_DIR)

mypy:
	mypy $(SRC_DIR)

package:
	rm dist/*
	python3 setup.py sdist

upload:
	twine upload dist/*