package:
	rm dist/*
	@python setup.py sdist

upload:
	pipenv run twine upload dist/*