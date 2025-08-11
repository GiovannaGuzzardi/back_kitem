from rest_framework import serializers
from django.contrib.auth.models import User as Usuario
from .models import ListaItens, ListaItensIngrediente

# Serializer para o modelo ListaItens (mantendo compatibilidade com ListaCompras)
class ListaItensSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaItens
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'id_usuario': {'required': True}  # Campo obrigatório
        }

# Serializer para o modelo ListaItensIngrediente (mantendo compatibilidade com ListaComprasIngrediente)
class ListaItensIngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaItensIngrediente
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'id_ingrediente': {'required': True},  # Campo obrigatório
            'id_lista': {'required': True},  # Campo obrigatório
            'quantidade': {
                'required': True,
                'error_messages': {
                    'invalid': 'A quantidade deve ser um número válido.'
                }
            },
            'unidade_medida': {
                'required': True,
                'error_messages': {
                    'blank': 'A unidade de medida não pode estar vazia.',
                    'required': 'A unidade de medida é obrigatória.'
                }
            },
            'preco': {
                'required': False,  # Campo opcional
                'error_messages': {
                    'invalid': 'O preço deve ser um número decimal válido.'
                }
            }
        }

# Aliases para manter compatibilidade com nomenclatura antiga
ListaComprasSerializer = ListaItensSerializer
ListaComprasIngredienteSerializer = ListaItensIngredienteSerializer
