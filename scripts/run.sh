#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --no-input
python manage.py migrate

uwsgi --socket :8080 --workers 1 --master --enable-threads --module core.wsgi
