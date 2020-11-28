package:
	pipenv-setup sync
	@python setup.py sdist

upload:
	twine upload dist/*