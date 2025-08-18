# criar projeto
python -m django startproject Kitem 
pip install pygments 
pip install djangorestframework

# venv -> ambiente virtual
python -m venv env
.\env\Scripts\Activate.ps1

# comandos basicos
python manage.py migrate Kitem -> modificações
python manage.py makemigrations Kitem -> persistir modificações
python manage.py runserver -> rodar back-end localmente em modo de desenvolvedor

# Explicação do codigo
