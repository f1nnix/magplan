dev:
	pipenv install --dev
	export $(grep -v '^#' .env/dev | xargs)
	pipenv run python ./manage.py runserver
deploy:
	ansible-playbook ansible/main.yml