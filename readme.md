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
Nesse projeto foi utilizada a arquitetura **Django REST Framework (DRF) modularizada por apps** que torna o codigo organizado e escalável.

Kitem/

├── favorito/            # App de gerenciamento de favoritos

├── ingrediente/         # App de gerenciamento de ingredientes

├── KiItem/              # App principal e configurações do projeto

├── lista_itens/         # App de gerenciamento de listas de itens

├── receita/             # App de gerenciamento de receitas

├── manage.py            # Script de gerenciamento do Django

├── requirements.txt     # Dependências do projeto

└── SWAGGER_README.md    # Documentação detalhada da API (Swagger)

## A estrutura é composta por:
  ### App principal: 
  kiItem: Responsável pela configuração central da aplicação e integração entre os diferentes módulos do sistema.
  ### Apps secundários: 
  Representam as diferentes entidades do sistema (como favorito, ingrediente, lista_itens, receita, etc.). Cada um desses apps funciona de forma independente, contendo seus próprios modelos, serializers, views e rotas, seguindo o princípio de separação de responsabilidades.
## Integração com o banco de dados
O sistema está integrado a um banco de dados relacional PostgreSQL, que foi hospedado na plataforma Aiven, um serviço de nuvem gerenciado. Essa integração garante maior desempenho, confiabilidade e disponibilidade dos dados, além de facilitar o deploy em ambientes online.
## API REST
A API foi construída com o Django REST Framework (DRF), permitindo a criação de endpoints RESTful robustos e seguros, que seguem boas práticas de desenvolvimento backend. A modularização por apps facilita tanto a manutenção quanto a expansão futura do sistema, como a adição de novos módulos ou funcionalidades.
## swagger
Foi adicionado um swagger para melhor visualização na hora de consumir os dados pelo front-end que esta melhor documentado no seu readme especifico
