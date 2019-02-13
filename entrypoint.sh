#!/bin/bash
python manage.py makemigrations
python manage.py migrate
if [[ $1 == "test" ]]; then
  python manage.py test  
else
  python manage.py runserver 0.0.0.0:80
fi
