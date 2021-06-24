package:
	rm dist/*
	python3 setup.py sdist

upload:
	twine upload dist/*