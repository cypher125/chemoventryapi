#!/bin/bash

# install dependancies
pip install setuptools
pip install -r requirement.txt


# Run django commands
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic