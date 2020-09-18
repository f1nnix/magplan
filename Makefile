migrate:
	@python ./manage.py makemigrations
	@python ./manage.py migrate

dev:
	export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/
	pipenv install --dev
	export $(grep -v '^#' .env/dev | xargs)
	pipenv run python ./manage.py runserver

deploy:
	ansible-playbook ansible/main.yml

test:
	export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/
	pipenv install --dev
	export $(grep -v '^#' .env/dev | xargs)
	pipenv run pytest -sq

stage-production-dependancies:
	export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/
	rm -rf `pipenv --venv`
	pipenv install
	pipenv run pip freeze > requirements.txt
