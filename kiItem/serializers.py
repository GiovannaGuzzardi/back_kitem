from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as Usuario

from ingrediente.models import Ingrediente
from receita.models import Receita, ReceitaIngrediente
from favorito.models import Favorito
from lista_itens.models import ListaItens, ListaItensIngrediente

# Configuração do modelo de usuário
Usuario = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Adiciona informações extras ao token, se desejar
        token['id'] = user.id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Adiciona o ID do usuário na resposta (fora do token também, se quiser)
        data['user_id'] = self.user.id
        return data

# Serializer para o modelo Usuario (Django User)
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'username': {
                'required': True,
                'error_messages': {
                    'blank': 'O nome de usuário não pode estar vazio.',
                    'required': 'O nome de usuário é obrigatório.',
                    'max_length': 'O nome de usuário não pode ter mais de 150 caracteres.'
                }
            }
        }

    def create(self, validated_data):
        # Removendo a senha do validated_data para tratá-la separadamente
        password = validated_data.pop('password')
        
        # Criando o usuário (sem definir a senha ainda)
        user = Usuario(**validated_data)
        
        # Definindo a senha corretamente (hash)
        user.set_password(password)

        # Garantindo que seja um usuário comum
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True

        # Salvando no banco
        user.save()
        return user


# Serializer para o modelo Ingrediente
class IngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingrediente
        fields = '__all__'  # Inclui todos os campos do modelo
        extra_kwargs = {
            'id': {'read_only': True},  # O campo 'id' é somente leitura
            'nome': {
                'required': True,  # O campo 'nome' é obrigatório
                'error_messages': {  # Mensagens de erro personalizadas
                    'blank': 'O nome do ingrediente não pode estar vazio.',
                    'required': 'O nome do ingrediente é obrigatório.',
                    'max_length': 'O nome do ingrediente não pode ter mais de 50 caracteres.'
                }
            }
        }

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

# Serializer para o modelo ListaItens
class ListaItensSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaItens
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'id_usuario': {'required': True}  # Campo obrigatório
        }

# Serializer para o modelo ListaItensIngrediente
class ListaItensIngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaItensIngrediente
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'id_ingrediente': {'required': True},  # Campo obrigatório
            'id_lista_itens': {'required': True},  # Campo obrigatório
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

# Aliases para manter compatibilidade com nomenclatura anterior
class ListaComprasSerializer(ListaItensSerializer):
    """Alias para compatibilidade com API anterior"""
    pass

class ListaComprasIngredienteSerializer(ListaItensIngredienteSerializer):
    """Alias para compatibilidade com API anterior"""
    pass
