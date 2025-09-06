from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiParameter, OpenApiTypes
from .models import Denuncia
from .serializers import DenunciaSerializer, DenunciaListSerializer

@extend_schema_view(
    list=extend_schema(
        tags=['denuncias'],
        summary='Listar denúncias (ViewSet)',
        description='Lista todas as denúncias usando ViewSet'
    ),
    create=extend_schema(
        tags=['denuncias'],
        summary='Criar denúncia (ViewSet)',
        description='Cria nova denúncia usando ViewSet'
    ),
    retrieve=extend_schema(
        tags=['denuncias'],
        summary='Detalhar denúncia (ViewSet)',
        description='Retorna detalhes de uma denúncia específica'
    ),
    update=extend_schema(
        tags=['denuncias'],
        summary='Atualizar denúncia (ViewSet)',
        description='Atualiza denúncia específica'
    ),
    partial_update=extend_schema(
        tags=['denuncias'],
        summary='Atualizar parcial denúncia (ViewSet)',
        description='Atualização parcial de denúncia'
    ),
    destroy=extend_schema(
        tags=['denuncias'],
        summary='Deletar denúncia (ViewSet)',
        description='Remove denúncia do sistema'
    ),
)
class DenunciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD completas em denúncias.
    """
    queryset = Denuncia.objects.all().select_related('id_receita', 'id_denunciante')
    serializer_class = DenunciaSerializer
    lookup_field = 'unique_id'
    
    def get_serializer_class(self):
        """Usa serializer simplificado para listagem"""
        if self.action == 'list':
            return DenunciaListSerializer
        return DenunciaSerializer
    
    def create(self, request, *args, **kwargs):
        """Criação de denúncia com validações extras"""
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response(
                {"error": "Erro de validação", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        tags=['denuncias'],
        summary='Denúncias por receita (Action)',
        description='Lista denúncias de uma receita específica via action do ViewSet',
        parameters=[
            OpenApiParameter(
                name='receita_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID da receita'
            ),
        ]
    )
    @action(detail=False, methods=['get'], url_path='por-receita/(?P<receita_id>[^/.]+)')
    def por_receita(self, request, receita_id=None):
        """Lista todas as denúncias de uma receita específica"""
        try:
            denuncias = self.queryset.filter(id_receita=receita_id)
            serializer = DenunciaListSerializer(denuncias, many=True)
            return Response({
                "receita_id": receita_id,
                "total_denuncias": denuncias.count(),
                "denuncias": serializer.data
            })
        except Exception as e:
            return Response(
                {"error": f"Erro ao buscar denúncias da receita: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        tags=['denuncias'],
        summary='Denúncias por usuário (Action)',
        description='Lista denúncias feitas por um usuário específico via action do ViewSet',
        parameters=[
            OpenApiParameter(
                name='usuario_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID do usuário'
            ),
        ]
    )
    @action(detail=False, methods=['get'], url_path='por-usuario/(?P<usuario_id>[^/.]+)')
    def por_usuario(self, request, usuario_id=None):
        """Lista todas as denúncias feitas por um usuário"""
        try:
            denuncias = self.queryset.filter(id_denunciante=usuario_id)
            serializer = DenunciaListSerializer(denuncias, many=True)
            return Response({
                "usuario_id": usuario_id,
                "total_denuncias": denuncias.count(),
                "denuncias": serializer.data
            })
        except Exception as e:
            return Response(
                {"error": f"Erro ao buscar denúncias do usuário: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        tags=['denuncias'],
        summary='Estatísticas de denúncias (Action)',
        description='Retorna estatísticas gerais das denúncias via action do ViewSet'
    )
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Estatísticas gerais das denúncias"""
        try:
            total_denuncias = self.queryset.count()
            
            # Estatísticas por motivo
            stats_motivo = self.queryset.values('motivo_denuncia').annotate(
                count=Count('motivo_denuncia')
            ).order_by('-count')
            
            # Converte números em texto legível
            motivos_stats = []
            for stat in stats_motivo:
                motivo_texto = dict(Denuncia.MOTIVO_CHOICES).get(stat['motivo_denuncia'], 'Desconhecido')
                motivos_stats.append({
                    'motivo': motivo_texto,
                    'quantidade': stat['count']
                })
            
            # Receitas mais denunciadas
            receitas_denunciadas = self.queryset.values(
                'id_receita__titulo', 'id_receita'
            ).annotate(
                count=Count('id_receita')
            ).order_by('-count')[:10]
            
            return Response({
                "total_denuncias": total_denuncias,
                "estatisticas_por_motivo": motivos_stats,
                "receitas_mais_denunciadas": list(receitas_denunciadas)
            })
        except Exception as e:
            return Response(
                {"error": f"Erro ao calcular estatísticas: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
