from rest_framework import serializers
from django.contrib.auth.models import User as Usuario
from .models import Receita, ReceitaIngrediente

# Serializer para o modelo Receita
class ReceitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receita
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'titulo': {
                'required': True,
                'error_messages': {
                    'blank': 'O título da receita não pode estar vazio.',
                    'required': 'O título da receita é obrigatório.',
                    'max_length': 'O título da receita não pode ter mais de 50 caracteres.'
                }
            },
            'descricao': {
                'required': True,
                'error_messages': {
                    'blank': 'A descrição não pode estar vazia.',
                    'required': 'A descrição é obrigatória.',
                    'max_length': 'A descrição não pode ter mais de 255 caracteres.'
                }
            },
            'tempo_preparo': {'required': True},  # Campo obrigatório
            'dificuldade': {'required': True},  # Campo obrigatório
            'quantidade_visualizacao': {'read_only': True}  # Somente leitura
        }

# Serializer para o modelo ReceitaIngrediente
class ReceitaIngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceitaIngrediente
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'id_ingrediente': {'required': True},  # Campo obrigatório
            'id_receita': {'required': True},  # Campo obrigatório
            'quantidade': {
                'required': True,
                'error_messages': {
                    'invalid': 'A quantidade deve ser um número válido.'  # Mensagem de erro personalizada
                }
            },
            'unidade_medida': {
                'required': True,
                'error_messages': {
                    'blank': 'A unidade de medida não pode estar vazia.',
                    'required': 'A unidade de medida é obrigatória.'
                }
            }
        }
