from rest_framework import serializers
from django.contrib.auth.models import User as Usuario
from .models import Favorito

# Serializer para o modelo Favorito
class FavoritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorito
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'id_receita': {'required': True},  # Campo obrigatório
            'id_usuario': {'required': True}  # Campo obrigatório
        }
