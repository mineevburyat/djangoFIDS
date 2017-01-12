#!/bin/sh
cd flightinfosystem/migrations/
ls | grep -v __init__.py | xargs rm -rfv
cd ../..
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py loaddata airline
python3 manage.py loaddata boards
python3 manage.py loaddata chekins
python3 manage.py loaddata events
python3 manage.py loaddata baggege
python3 manage.py loaddata codeshar
python3 manage.py createsuperuser
python3 manage.py getxml
#sudo crontab -e
echo "Install pytz?"
echo "Install pil?"