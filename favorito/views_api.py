from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from .models import Favorito
from kiItem.serializers import FavoritoSerializer

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint para favoritos
    """
    return Response({
        'favoritos': request.build_absolute_uri('/api/favoritos/'),
    })

# Views para a API de Favoritos
class FavoritoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Favorito.objects.all()
    serializer_class = FavoritoSerializer

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

class GetFavoritoUsuario(generics.ListAPIView):
    serializer_class = FavoritoSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']  # Pega o valor <user_id> da URL
        return Favorito.objects.filter(id_usuario=user_id)

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
                    "data_favorito": favorito.data_favorito,
                })

            return Response(data)

        except Exception as e:
            return Response({"error": f"Erro ao buscar favoritos: {str(e)}"}, status=500)

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
class ReceitasFavoritasAPIView(generics.ListAPIView):
    serializer_class = FavoritoSerializer
    
    def get_queryset(self):
        id_usuario = self.kwargs['id_usuario']
        return Favorito.objects.filter(id_usuario=id_usuario)
