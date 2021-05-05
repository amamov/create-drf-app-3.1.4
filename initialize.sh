#!/bin/sh

echo "Hello master."

echo "You should already have docker-compose installed. If it is not installed, install it."

rm -rf .git

echo "SECRET_KEY=change_this_value\nDB_HOST=localhost\nDB_NAME=mydb\nDB_USER=admin\nDB_PORT=3307\nDB_PASSWORD=1205" > .env

docker-compose up -d --build

echo "Activate your Python virtual environment."
echo "Is the activated virtual environment pipenv? (y/n)"
echo "If you don't know pipenv well, say 'n' and press enter."
read answer
if [ $answer = "y" ] || [ $answer = "Y" ];
then
  pipenv shell
  pipenv install -r requirements.txt
else
  pip3 install -r requirements.txt
fi
python3 manage.py migrate
echo "Create a superuser."
python3 manage.py createsuperuser
echo "Hack your life :)"
python3 manage.py runserver

exit 0
