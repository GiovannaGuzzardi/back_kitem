<!-- criar projeto -->
python -m django startproject Kitem 
pip install pygments 
.\env\Scripts\Activate.ps1
python -m venv env
pip install djangorestframework
python manage.py startapp Kitem
python manage.py migrate Kitem
python manage.py makemigrations Kitem 
python manage.py runserver