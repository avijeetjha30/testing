.PHONY: install_packages
install_packages:
	poetry install

.PHONY: flake
flake:
	poetry run flake8

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: runserver
runserver:
	poetry run python3 -m core.manage runserver 0.0.0.0:3030

.PHONY: makemigrations
makemigrations:
	poetry run python3 -m core.manage makemigrations

.PHONY: migrate
migrate:
	poetry run python3 -m core.manage migrate

.PHONY: startapp
startapp:
	poetry run python3 -m core.manage startapp $(argument)

.PHONY: createsuperuser
createsuperuser:
	poetry run python3 -m core.manage createsuperuser

.PHONY: up-dependencies-only
up-dependencies-only:
	test -f .env || touch .env
	docker compose -f docker-compose.dev.yml up -d --force-recreate db

.PHONY: script
script: install_packages makemigrations migrate install-pre-commit;
