#!/bin/bash

if [ -z "$1" ]
  then
    echo "No argument supplied"
    exit 1
elif [ $1 = "migrate" ]
  then
      python manage.py migrate
      python manage.py load_data ingredients.json
elif [ $1 = "pre-run" ]
  then
      python manage.py collectstatic --noinput
elif [ $1 = "run" ]
  then
    exec $(which gunicorn) foodgram.wsgi:application --bind=0:8000
    exit $?
elif [ $1 = "all" ]
  then
      python manage.py migrate
      python manage.py load_data ingredients.json
      python manage.py collectstatic --noinput
    exec $(which gunicorn) foodgram.wsgi:application --bind=0:8000
    exit $?
else
  echo "Invalid argument"
  exit 1
fi
