#!/bin/sh
python3 manage.py loaddata boards
python3 manage.py loaddata chekins
python3 manage.py loaddata events
python3 manage.py loaddata baggege
python3 manage.py createsuperuser
python3 manage.py getxml


echo "Install pytz?"
echo "Install pil?"