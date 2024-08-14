#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install pipenv if not installed
pip install pipenv

# Install dependencies
pipenv install

# Apply any outstanding database migrations
python manage.py migrate
