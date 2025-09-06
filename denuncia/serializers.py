from rest_framework import serializers
from django.contrib.auth.models import User
from receita.models import Receita
from .models import Denuncia

class DenunciaSerializer(serializers.ModelSerializer):
    # Campos adicionais para exibição
    motivo_denuncia_display = serializers.CharField(source='get_motivo_denuncia_display', read_only=True)
    denunciante_username = serializers.CharField(source='id_denunciante.username', read_only=True)
    receita_titulo = serializers.CharField(source='id_receita.titulo', read_only=True)
    
    class Meta:
        model = Denuncia
        fields = [
            'unique_id',
            'id_receita',
            'motivo_denuncia',
            'motivo_denuncia_display',
            'detalhamento',
            'id_denunciante',
            'denunciante_username',
            'receita_titulo',
            'data_denuncia'
        ]
        extra_kwargs = {
            'unique_id': {'read_only': True},
            'data_denuncia': {'read_only': True},
            'id_receita': {
                'required': True,
                'error_messages': {
                    'required': 'A receita é obrigatória.',
                    'does_not_exist': 'Receita não encontrada.'
                }
            },
            'motivo_denuncia': {
                'required': True,
                'error_messages': {
                    'required': 'O motivo da denúncia é obrigatório.',
                    'invalid_choice': 'Motivo de denúncia inválido.'
                }
            },
            'id_denunciante': {
                'required': True,
                'error_messages': {
                    'required': 'O denunciante é obrigatório.',
                    'does_not_exist': 'Usuário não encontrado.'
                }
            },
            'detalhamento': {
                'required': False,
                'allow_blank': True,
                'error_messages': {
                    'max_length': 'O detalhamento não pode ter mais de 280 caracteres.'
                }
            }
        }
    
    def validate_motivo_denuncia(self, value):
        """Valida se o motivo da denúncia é válido"""
        valid_motivos = [choice[0] for choice in Denuncia.MOTIVO_CHOICES]
        if value not in valid_motivos:
            raise serializers.ValidationError("Motivo de denúncia inválido.")
        return value
    
    def validate_detalhamento(self, value):
        """Valida o detalhamento da denúncia"""
        if value and len(value.strip()) == 0:
            return None  # Converte string vazia em None
        return value
    
    def validate(self, data):
        """Validação customizada para evitar denúncias duplicadas"""
        id_receita = data.get('id_receita')
        id_denunciante = data.get('id_denunciante')
        
        # Verifica se já existe uma denúncia desta receita por este usuário
        if self.instance is None:  # Apenas para criação, não para atualização
            if Denuncia.objects.filter(id_receita=id_receita, id_denunciante=id_denunciante).exists():
                raise serializers.ValidationError({
                    'non_field_errors': ['Você já denunciou esta receita anteriormente.']
                })
        
        return data

# Serializer simplificado para listagem
class DenunciaListSerializer(serializers.ModelSerializer):
    motivo_denuncia_display = serializers.CharField(source='get_motivo_denuncia_display', read_only=True)
    denunciante_username = serializers.CharField(source='id_denunciante.username', read_only=True)
    receita_titulo = serializers.CharField(source='id_receita.titulo', read_only=True)
    
    class Meta:
        model = Denuncia
        fields = [
            'unique_id',
            'motivo_denuncia',
            'motivo_denuncia_display',
            'denunciante_username',
            'receita_titulo',
            'data_denuncia'
        ]
