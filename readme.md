<!-- criar projeto -->
python -m django startproject kiItem 
pip install pygments 
source env/bin/activate
python -m venv env
pip install djangorestframework
python manage.py startapp kiItem
python manage.py migrate myApp
python manage.py makemigrations myApp 
python manage.py runserver