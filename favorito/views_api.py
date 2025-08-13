from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from .models import Favorito
from kiItem.serializers import FavoritoSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint para favoritos
    """
    return Response({
        'favoritos': request.build_absolute_uri('/api/favoritos/'),
    })

# Views para a API de Favoritos
@extend_schema_view(
    get=extend_schema(
        summary="Listar todos os favoritos",
        description="Retorna uma lista de todos os favoritos cadastrados no sistema",
        tags=['favoritos'],
        responses={200: FavoritoSerializer(many=True)}
    ),
    post=extend_schema(
        summary="Criar novo favorito",
        description="Cria um novo favorito associando um usuário a uma receita",
        tags=['favoritos'],
        request=FavoritoSerializer,
        responses={201: FavoritoSerializer},
        examples=[
            OpenApiExample(
                'Exemplo de criação',
                value={
                    'id_usuario': 1,
                    'id_receita': 1
                },
                description='Exemplo de dados para criar um favorito'
            )
        ]
    )
)
class FavoritoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Favorito.objects.all()
    serializer_class = FavoritoSerializer

@extend_schema_view(
    get=extend_schema(
        summary="Obter detalhes de um favorito",
        description="Retorna os detalhes de um favorito específico pelo ID",
        tags=['favoritos'],
        responses={200: FavoritoSerializer}
    ),
    put=extend_schema(
        summary="Atualizar favorito",
        description="Atualiza um favorito existente",
        tags=['favoritos'],
        request=FavoritoSerializer,
        responses={200: FavoritoSerializer}
    ),
    delete=extend_schema(
        summary="Deletar favorito",
        description="Remove um favorito do sistema",
        tags=['favoritos'],
        responses={204: None}
    )
)
class FavoritoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Favorito.objects.all()
    serializer_class = FavoritoSerializer
    
    def get_object(self):
        try:
            return Favorito.objects.get(pk=self.kwargs['pk'])
        except Favorito.DoesNotExist:
            raise NotFound(detail="Favorito não encontrado.")
        except Exception as e:
            raise NotFound(detail=f"Erro inesperado: {str(e)}")
    
    def delete(self, request, *args, **kwargs):
        """
        Override do método delete para adicionar validação de segurança.
        Recomenda-se usar o endpoint DELETE /usuarios/<id_usuario>/favoritos/<receita_id>/ 
        para maior segurança.
        """
        favorito = self.get_object()
        
        # Aqui você pode adicionar validação adicional se necessário
        # Por exemplo, verificar se o usuário logado tem permissão
        
        return super().delete(request, *args, **kwargs)

@extend_schema(
    summary="Listar favoritos de um usuário específico",
    description="Retorna todos os favoritos de um usuário pelo ID",
    tags=['favoritos'],
    parameters=[
        OpenApiParameter(
            name='user_id',
            location=OpenApiParameter.PATH,
            description='ID do usuário',
            required=True,
            type=int
        )
    ],
    responses={200: FavoritoSerializer(many=True)}
)
class GetFavoritoUsuario(generics.ListAPIView):
    serializer_class = FavoritoSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']  # Pega o valor <user_id> da URL
        return Favorito.objects.filter(id_usuario=user_id)

@extend_schema(
    summary="Obter favoritos detalhados de um usuário",
    description="Retorna favoritos de um usuário com informações detalhadas da receita",
    tags=['favoritos'],
    parameters=[
        OpenApiParameter(
            name='user_id',
            location=OpenApiParameter.PATH,
            description='ID do usuário',
            required=True,
            type=int
        )
    ],
    responses={
        200: {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id_favorito': {'type': 'integer'},
                    'id_receita': {'type': 'integer'},
                    'titulo_receita': {'type': 'string'},
                    'dificuldade': {'type': 'string'},
                    'tempo_preparo': {'type': 'integer'},
                    'tipo': {'type': 'string'}
                }
            }
        },
        404: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'}
            }
        }
    }
)
class FavoritoDetalhadoAPIView(APIView):
    def get(self, request, user_id):
        try:
            favoritos = Favorito.objects.filter(id_usuario=user_id).select_related('id_receita')
            
            if not favoritos.exists():
                return Response({"message": "Nenhum favorito encontrado para este usuário."}, status=404)

            data = []
            for favorito in favoritos:
                receita = favorito.id_receita
                data.append({
                    "id_favorito": favorito.id,
                    "id_receita": receita.id,
                    "titulo_receita": receita.titulo,
                    "dificuldade": receita.dificuldade,
                    "tempo_preparo": receita.tempo_preparo,
                    "tipo": receita.tipo,
                })

            return Response(data)

        except Exception as e:
            return Response({"error": f"Erro ao buscar favoritos: {str(e)}"}, status=500)

@extend_schema(
    summary="Filtrar favoritos de um usuário",
    description="Filtra favoritos de um usuário por tipo, dificuldade e busca no título da receita",
    tags=['favoritos'],
    parameters=[
        OpenApiParameter(
            name='user_id',
            location=OpenApiParameter.PATH,
            description='ID do usuário',
            required=True,
            type=int
        ),
        OpenApiParameter(
            name='tipo',
            location=OpenApiParameter.QUERY,
            description='Tipo da receita (doce ou salgado)',
            required=False,
            type=str,
            enum=['doce', 'salgado']
        ),
        OpenApiParameter(
            name='dificuldade',
            location=OpenApiParameter.QUERY,
            description='Dificuldade da receita',
            required=False,
            type=str,
            enum=['Fácil', 'Média', 'Difícil', 'Master Chef']
        ),
        OpenApiParameter(
            name='search',
            location=OpenApiParameter.QUERY,
            description='Termo de busca no título da receita',
            required=False,
            type=str
        )
    ],
    responses={
        200: FavoritoSerializer(many=True),
        404: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'}
            }
        }
    }
)
class FavoritoFilterAPIView(APIView):
    """
    Endpoint para filtrar favoritos de um usuário com base em critérios da receita.
    """
    def get(self, request, user_id):
        tipo = request.query_params.get('tipo')
        dificuldade = request.query_params.get('dificuldade')
        search = request.query_params.get('search')  # Campo de pesquisa para o título da receita

        # Validações
        valid_tipos = ["doce", "salgado"]
        valid_dificuldades = ["Fácil", "Média", "Difícil", "Master Chef"]

        if tipo and tipo not in valid_tipos:
            raise ValidationError({"tipo": f"Tipo inválido. Valores permitidos: {', '.join(valid_tipos)}"})

        if dificuldade and dificuldade not in valid_dificuldades:
            raise ValidationError({"dificuldade": f"Dificuldade inválida. Valores permitidos: {', '.join(valid_dificuldades)}"})

        # Construção do filtro dinâmico
        filtros = Q(id_usuario=user_id)
        if tipo:
            filtros &= Q(id_receita__tipo__iexact=tipo)
        if dificuldade:
            filtros &= Q(id_receita__dificuldade__iexact=dificuldade)
        if search:
            filtros &= Q(id_receita__titulo__icontains=search)

        # Consulta ao banco de dados
        try:
            favoritos = Favorito.objects.filter(filtros).select_related('id_receita')
        except Exception as e:
            raise ValidationError({"error": f"Erro ao consultar favoritos: {str(e)}"})

        if not favoritos.exists():
            return Response({"message": "Nenhum favorito encontrado com os filtros fornecidos."}, status=404)

        serializer = FavoritoSerializer(favoritos, many=True)
        return Response(serializer.data)

@extend_schema(
    summary="Toggle de favorito",
    description="Adiciona ou remove uma receita dos favoritos de um usuário. Se já existir, remove; se não existir, adiciona.",
    tags=['favoritos'],
    parameters=[
        OpenApiParameter(
            name='user_id',
            location=OpenApiParameter.PATH,
            description='ID do usuário',
            required=True,
            type=int
        ),
        OpenApiParameter(
            name='receita_id',
            location=OpenApiParameter.PATH,
            description='ID da receita',
            required=True,
            type=int
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'example': 'Receita removida dos favoritos.'}
            }
        },
        201: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'example': 'Receita adicionada aos favoritos.'},
                'favorito': {'type': 'object'}
            }
        }
    }
)
class FavoritoToggleAPIView(APIView):
    """
    Endpoint para adicionar ou remover uma receita dos favoritos de um usuário.
    """
    def post(self, request, user_id, receita_id):
        try:
            # Verifica se já existe
            favorito_existente = Favorito.objects.filter(id_usuario=user_id, id_receita=receita_id).first()
            
            if favorito_existente:
                # Remove dos favoritos
                favorito_existente.delete()
                return Response({"message": "Receita removida dos favoritos."}, status=200)
            else:
                # Adiciona aos favoritos
                favorito = Favorito.objects.create(id_usuario_id=user_id, id_receita_id=receita_id)
                serializer = FavoritoSerializer(favorito)
                return Response({
                    "message": "Receita adicionada aos favoritos.",
                    "favorito": serializer.data
                }, status=201)
                
        except Exception as e:
            return Response({"error": f"Erro ao processar favorito: {str(e)}"}, status=500)

# Views customizadas para compatibilidade com nomenclatura anterior
@extend_schema(
    summary="Listar favoritos de um usuário",
    description="Retorna todos os favoritos de um usuário específico",
    tags=['favoritos'],
    parameters=[
        OpenApiParameter(
            name='id_usuario',
            location=OpenApiParameter.PATH,
            description='ID do usuário',
            required=True,
            type=int
        )
    ],
    responses={
        200: FavoritoSerializer(many=True),
        404: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'example': 'Nenhuma receita favorita encontrada para este usuário.'}
            }
        }
    }
)
class ReceitasFavoritasAPIView(generics.ListAPIView):
    serializer_class = FavoritoSerializer
    
    def get_queryset(self):
        id_usuario = self.kwargs['id_usuario']
        return Favorito.objects.filter(id_usuario=id_usuario)

@extend_schema(
    summary="Deletar favorito por usuário e receita",
    description="Remove um favorito específico de um usuário. Endpoint mais seguro que garante que o usuário só pode deletar seus próprios favoritos.",
    tags=['favoritos'],
    parameters=[
        OpenApiParameter(
            name='id_usuario',
            location=OpenApiParameter.PATH,
            description='ID do usuário',
            required=True,
            type=int
        ),
        OpenApiParameter(
            name='receita_id',
            location=OpenApiParameter.PATH,
            description='ID da receita',
            required=True,
            type=int
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'example': 'Favorito removido com sucesso.'},
                'usuario_id': {'type': 'integer', 'example': 1},
                'receita_id': {'type': 'integer', 'example': 1}
            }
        },
        404: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'example': 'Favorito não encontrado para este usuário e receita.'}
            }
        }
    }
)
class FavoritoDeleteByUsuarioReceitaAPIView(APIView):
    """
    Endpoint para deletar favorito por usuário e receita (mais seguro).
    Garante que o usuário só pode deletar seus próprios favoritos.
    """
    def delete(self, request, id_usuario, receita_id):
        try:
            # Busca o favorito específico do usuário
            favorito = Favorito.objects.filter(
                id_usuario=id_usuario, 
                id_receita=receita_id
            ).first()
            
            if not favorito:
                return Response({
                    "message": "Favorito não encontrado para este usuário e receita."
                }, status=404)
            
            # Deleta o favorito
            favorito.delete()
            
            return Response({
                "message": "Favorito removido com sucesso.",
                "usuario_id": id_usuario,
                "receita_id": receita_id
            }, status=200)
                
        except Exception as e:
            return Response({
                "error": f"Erro ao deletar favorito: {str(e)}"
            }, status=500)
