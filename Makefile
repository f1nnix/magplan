package:
	pipenv-setup sync
	rm dist/*
	@python setup.py sdist

upload:
	twine upload dist/*