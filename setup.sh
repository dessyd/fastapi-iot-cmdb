#!/bin/bash
# Install Postgres
brew install postgresql
# Create virtual environment
python3 -m venv .venv
# Activate it
source .venv/bin/activate
# make sure pip is up to date
pip install --upgrade pip
# install project's requirements
pip install -r requirements.txt
# Install pre-commit
pre-commit install
# Auto update to latest hooks
pre-commit autoupdate
# Have a first test
pre-commit run --all-files
