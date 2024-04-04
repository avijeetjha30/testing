project setup
=============

Project setup instructions here.

1. create and activate virtual environment
    in ubuntu
        python3 -m venv .venv
        source .venv/bin/activate
    in windows
        python3 -m venv .venv
        source .venv/script/activate


2.  install poetry:
        -> https://python-poetry.org/docs/#installing-with-the-official-installer
    check poetry version:
        -> poetry --version
    generate pyproject.toml file for project package management and more. For more information read docs https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/
        -> poetry install

3.  https://github.com/wemake-services/django-split-settings

4. mkdir local

5. cp -r core/project/settings/templates/settings.dev.py ./local/settings.dev.py

6.
