#!/bin/bash

apt-get update

apt-get install -y firefox-esr

pyhton manage.py collectstatic --noinput

gunicorn amazon_scrapper.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 600
