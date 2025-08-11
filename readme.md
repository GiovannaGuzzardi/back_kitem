<!-- criar projeto -->
python -m django startproject kiItem 
pip install pygments 
.\env\Scripts\Activate.ps1
python -m venv env
pip install djangorestframework
python manage.py startapp kiItem
python manage.py migrate kiItem
python manage.py makemigrations kiItem 
python manage.py runserver