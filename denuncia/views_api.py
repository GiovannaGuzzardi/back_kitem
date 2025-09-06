from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.db.models import Q, Count
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiParameter, OpenApiTypes
from .models import Denuncia
from .serializers import DenunciaSerializer, DenunciaListSerializer

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint para denúncias
    """
    return Response({
        'denuncias': request.build_absolute_uri('/api/denuncias/'),
        'denuncias_por_receita': request.build_absolute_uri('/api/denuncias/receita/{receita_id}/'),
        'denuncias_por_usuario': request.build_absolute_uri('/api/denuncias/usuario/{usuario_id}/'),
        'estatisticas_denuncias': request.build_absolute_uri('/api/denuncias/estatisticas/'),
        'filtrar_denuncias': request.build_absolute_uri('/api/denuncias/filtrar/'),
    })

# Views para a API de Denúncias
@extend_schema_view(
    list=extend_schema(
        tags=['denuncias'],
        summary='Listar todas as denúncias',
        description='Retorna uma lista paginada de todas as denúncias do sistema'
    ),
    create=extend_schema(
        tags=['denuncias'],
        summary='Criar nova denúncia',
        description='Cria uma nova denúncia para uma receita específica'
    ),
)
class DenunciaListCreateAPIView(generics.ListCreateAPIView):
    """
    Lista todas as denúncias ou cria uma nova denúncia
    """
    queryset = Denuncia.objects.all().select_related('id_receita', 'id_denunciante')
    serializer_class = DenunciaSerializer
    
    def get_serializer_class(self):
        """Usa serializer simplificado para listagem"""
        if self.request.method == 'GET':
            return DenunciaListSerializer
        return DenunciaSerializer

@extend_schema_view(
    retrieve=extend_schema(
        tags=['denuncias'],
        summary='Detalhar denúncia específica',
        description='Retorna os detalhes completos de uma denúncia específica pelo UUID'
    ),
    update=extend_schema(
        tags=['denuncias'],
        summary='Atualizar denúncia completa',
        description='Atualiza todos os campos de uma denúncia específica'
    ),
    partial_update=extend_schema(
        tags=['denuncias'],
        summary='Atualizar denúncia parcial',
        description='Atualiza campos específicos de uma denúncia'
    ),
    destroy=extend_schema(
        tags=['denuncias'],
        summary='Deletar denúncia',
        description='Remove uma denúncia do sistema'
    ),
)
class DenunciaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Recupera, atualiza ou deleta uma denúncia específica
    """
    queryset = Denuncia.objects.all().select_related('id_receita', 'id_denunciante')
    serializer_class = DenunciaSerializer
    lookup_field = 'unique_id'
    
    def get_object(self):
        try:
            return Denuncia.objects.select_related('id_receita', 'id_denunciante').get(
                unique_id=self.kwargs['unique_id']
            )
        except Denuncia.DoesNotExist:
            raise NotFound(detail="Denúncia não encontrada.")
        except Exception as e:
            raise NotFound(detail=f"Erro inesperado: {str(e)}")

@extend_schema(
    tags=['denuncias'],
    summary='Denúncias por receita',
    description='Lista todas as denúncias de uma receita específica',
    parameters=[
        OpenApiParameter(
            name='receita_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='ID da receita para buscar denúncias'
        ),
    ]
)
class DenunciasPorReceitaAPIView(generics.ListAPIView):
    """
    Lista todas as denúncias de uma receita específica
    """
    serializer_class = DenunciaListSerializer

    def get_queryset(self):
        receita_id = self.kwargs['receita_id']
        return Denuncia.objects.filter(id_receita=receita_id).select_related('id_receita', 'id_denunciante')

@extend_schema(
    tags=['denuncias'],
    summary='Denúncias por usuário',
    description='Lista todas as denúncias feitas por um usuário específico',
    parameters=[
        OpenApiParameter(
            name='usuario_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='ID do usuário para buscar denúncias feitas'
        ),
    ]
)
class DenunciasPorUsuarioAPIView(generics.ListAPIView):
    """
    Lista todas as denúncias feitas por um usuário específico
    """
    serializer_class = DenunciaListSerializer

    def get_queryset(self):
        usuario_id = self.kwargs['usuario_id']
        return Denuncia.objects.filter(id_denunciante=usuario_id).select_related('id_receita', 'id_denunciante')

@extend_schema(
    tags=['denuncias'],
    summary='Filtrar denúncias',
    description='Filtra denúncias com base em vários critérios como motivo, data, receita, etc.',
    parameters=[
        OpenApiParameter(
            name='motivo',
            type=OpenApiTypes.INT,
            description='Código do motivo da denúncia (1-7)'
        ),
        OpenApiParameter(
            name='receita_id',
            type=OpenApiTypes.INT,
            description='ID da receita específica'
        ),
        OpenApiParameter(
            name='usuario_id',
            type=OpenApiTypes.INT,
            description='ID do usuário denunciante'
        ),
        OpenApiParameter(
            name='data_inicio',
            type=OpenApiTypes.DATE,
            description='Data inicial para filtro (YYYY-MM-DD)'
        ),
        OpenApiParameter(
            name='data_fim',
            type=OpenApiTypes.DATE,
            description='Data final para filtro (YYYY-MM-DD)'
        ),
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            description='Busca no campo detalhamento'
        ),
    ]
)
class DenunciaFilterAPIView(APIView):
    """
    Endpoint para filtrar denúncias com base em motivo, data e receita.
    """
    def get(self, request):
        motivo = request.query_params.get('motivo')
        receita_id = request.query_params.get('receita_id')
        usuario_id = request.query_params.get('usuario_id')
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        search = request.query_params.get('search')  # Busca no detalhamento
        
        # Validações
        valid_motivos = [choice[0] for choice in Denuncia.MOTIVO_CHOICES]
        
        if motivo and int(motivo) not in valid_motivos:
            raise ValidationError({"motivo": f"Motivo inválido. Valores permitidos: {valid_motivos}"})
        
        # Construção do filtro dinâmico
        filtros = Q()
        if motivo:
            filtros &= Q(motivo_denuncia=int(motivo))
        if receita_id:
            filtros &= Q(id_receita=receita_id)
        if usuario_id:
            filtros &= Q(id_denunciante=usuario_id)
        if data_inicio:
            filtros &= Q(data_denuncia__gte=data_inicio)
        if data_fim:
            filtros &= Q(data_denuncia__lte=data_fim)
        if search:
            filtros &= Q(detalhamento__icontains=search)
        
        # Consulta ao banco de dados
        try:
            denuncias = Denuncia.objects.filter(filtros).select_related('id_receita', 'id_denunciante')
        except Exception as e:
            raise ValidationError({"error": f"Erro ao consultar denúncias: {str(e)}"})

        if not denuncias.exists():
            return Response({"message": "Nenhuma denúncia encontrada com os filtros fornecidos."}, status=404)

        serializer = DenunciaListSerializer(denuncias, many=True)
        return Response({
            "total_encontradas": denuncias.count(),
            "denuncias": serializer.data
        })

@extend_schema(
    tags=['denuncias'],
    summary='Estatísticas de denúncias',
    description='Retorna estatísticas gerais do sistema de denúncias, incluindo totais por motivo, receitas mais denunciadas, etc.'
)
class DenunciaEstatisticasAPIView(APIView):
    """
    Endpoint para obter estatísticas das denúncias.
    """
    def get(self, request):
        try:
            total_denuncias = Denuncia.objects.count()
            
            # Estatísticas por motivo
            stats_motivo = Denuncia.objects.values('motivo_denuncia').annotate(
                count=Count('motivo_denuncia')
            ).order_by('-count')
            
            # Converte números em texto legível
            motivos_stats = []
            for stat in stats_motivo:
                motivo_texto = dict(Denuncia.MOTIVO_CHOICES).get(stat['motivo_denuncia'], 'Desconhecido')
                motivos_stats.append({
                    'motivo_codigo': stat['motivo_denuncia'],
                    'motivo_texto': motivo_texto,
                    'quantidade': stat['count']
                })
            
            # Receitas mais denunciadas
            receitas_denunciadas = Denuncia.objects.values(
                'id_receita__titulo', 'id_receita'
            ).annotate(
                count=Count('id_receita')
            ).order_by('-count')[:10]
            
            # Usuários que mais denunciam
            usuarios_denunciantes = Denuncia.objects.values(
                'id_denunciante__username', 'id_denunciante'
            ).annotate(
                count=Count('id_denunciante')
            ).order_by('-count')[:10]

            data = {
                "total_denuncias": total_denuncias,
                "estatisticas_por_motivo": motivos_stats,
                "receitas_mais_denunciadas": list(receitas_denunciadas),
                "usuarios_que_mais_denunciam": list(usuarios_denunciantes),
                "motivos_disponiveis": [
                    {"codigo": codigo, "texto": texto} 
                    for codigo, texto in Denuncia.MOTIVO_CHOICES
                ]
            }

            return Response(data)

        except Exception as e:
            return Response({"error": f"Erro ao calcular estatísticas: {str(e)}"}, status=500)

class DenunciaToggleStatusAPIView(APIView):
    """
    Endpoint para marcar uma denúncia como resolvida/pendente (funcionalidade futura).
    """
    def patch(self, request, unique_id):
        try:
            denuncia = Denuncia.objects.get(unique_id=unique_id)
            
            # Por enquanto, apenas retorna informações da denúncia
            # No futuro, pode adicionar campo 'status' no modelo
            serializer = DenunciaSerializer(denuncia)
            return Response({
                "message": "Denúncia encontrada. Status toggle será implementado futuramente.",
                "denuncia": serializer.data
            })
            
        except Denuncia.DoesNotExist:
            raise NotFound(detail="Denúncia não encontrada.")
        except Exception as e:
            return Response({"error": f"Erro ao processar denúncia: {str(e)}"}, status=500)
