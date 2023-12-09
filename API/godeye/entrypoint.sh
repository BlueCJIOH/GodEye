#!/bin/bash

python manage.py migrate --fake-initial || exit 1
python manage.py runserver 0.0.0.0:8000