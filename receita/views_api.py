from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from random import sample
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from .models import Receita, ReceitaIngrediente
from favorito.models import Favorito
from kiItem.serializers import ReceitaSerializer, ReceitaIngredienteSerializer

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint para receitas
    """
    return Response({
        'receitas': request.build_absolute_uri('/api/receitas/'),
        'receita_ingredientes': request.build_absolute_uri('/api/receita_ingredientes/'),
    })

# Views para a API de Receitas
class ReceitaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Receita.objects.all()
    serializer_class = ReceitaSerializer

class ReceitaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Receita.objects.all()
    serializer_class = ReceitaSerializer
    def get_object(self):
        try:
            return Receita.objects.get(pk=self.kwargs['pk'])
        except Receita.DoesNotExist:
            raise NotFound(detail="Receita não encontrada.")
        except Exception as e:
            raise NotFound(detail=f"Erro inesperado: {str(e)}")

class GetReceitaUsuario(generics.ListAPIView):
    serializer_class = ReceitaSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']  # Pega o valor <user_id> da URL
        return Receita.objects.filter(id_usuario=user_id)

class ReceitaDetalhadaAPIView(APIView):
    def get(self, request, pk):
        try:
            receita = Receita.objects.get(pk=pk)
            ingredientes = ReceitaIngrediente.objects.filter(id_receita=receita).select_related('id_ingrediente')
            favoritos_count = Favorito.objects.filter(id_receita=receita).count()

            data = {
                "id_receita": receita.id,
                "titulo": receita.titulo,
                "dificuldade": receita.dificuldade,
                "ingredientes": [
                    {
                        "id_receita_ingrediente": ingrediente.id,
                        "quantidade": ingrediente.quantidade,
                        "unidade_medida": ingrediente.unidade_medida,
                        "nome_ingrediente": ingrediente.id_ingrediente.nome,
                    }
                    for ingrediente in ingredientes
                ],
                "favorito": favoritos_count,
            }

            return Response(data)

        except Receita.DoesNotExist:
            raise NotFound(detail="Receita não encontrada.")

@extend_schema(
    tags=['receitas'],
    summary="Filtrar receitas",
    description="Filtrar receitas por tipo, restrição alimentar, dificuldade, tempo de preparo, categoria, ingredientes e pesquisa por nome.",
    parameters=[
        OpenApiParameter(name='tipo', type=OpenApiTypes.STR, description='Tipo da receita (doce/salgado)'),
        OpenApiParameter(name='restricao_alimentar', type=OpenApiTypes.STR, description='Restrição alimentar'),
        OpenApiParameter(name='dificuldade', type=OpenApiTypes.STR, description='Nível de dificuldade'),
        OpenApiParameter(name='tempo_preparo', type=OpenApiTypes.INT, description='Tempo de preparo em minutos'),
        OpenApiParameter(name='categoria', type=OpenApiTypes.STR, description='Categoria da receita'),
        OpenApiParameter(name='ingredientes', type=OpenApiTypes.STR, description='Ingredientes (múltiplos valores)'),
        OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Busca por título da receita'),
    ]
)
class ReceitaFilterAPIView(APIView):
    """
    Endpoint para filtrar receitas com base em tipo, restrição alimentar, dificuldade, tempo de preparo e pesquisa por nome.
    """
    def get(self, request):
        tipo = request.query_params.get('tipo')
        restricoes_alimentares = request.query_params.getlist('restricao_alimentar')  # Aceita múltiplos valores
        dificuldade = request.query_params.get('dificuldade')
        tempo_preparo = request.query_params.get('tempo_preparo')
        tempo_preparo_operador = request.query_params.get('tempo_preparo_operador', 'menos')  # Padrão: "menos"
        search = request.query_params.get('search')  # Campo de pesquisa para o título da receita
        ingredientes = request.query_params.getlist('ingredientes')  # Aceita múltiplos valores para ingredientes
        categoria = request.query_params.get('categoria')  # Filtro por categoria
        
        # Validações
        valid_tipos = ["doce", "salgado"]
        valid_dificuldades = ["Fácil", "Média", "Difícil", "Master Chef"]
        valid_operadores = ["mais", "menos"]
        valid_categorias = [choice[0] for choice in Receita.CATEGORIA_CHOICES]

        if tipo and tipo not in valid_tipos:
            raise ValidationError({"tipo": f"Tipo inválido. Valores permitidos: {', '.join(valid_tipos)}"})

        if dificuldade and dificuldade not in valid_dificuldades:
            raise ValidationError({"dificuldade": f"Dificuldade inválida. Valores permitidos: {', '.join(valid_dificuldades)}"})

        if tempo_preparo_operador and tempo_preparo_operador not in valid_operadores:
            raise ValidationError({"tempo_preparo_operador": f"Operador inválido. Valores permitidos: {', '.join(valid_operadores)}"})

        if categoria and categoria not in valid_categorias:
            raise ValidationError({"categoria": f"Categoria inválida. Valores permitidos: {', '.join(valid_categorias)}"})

        # Validação de tempo de preparo
        if tempo_preparo:
            try:
                tempo_preparo = int(tempo_preparo)
                horas = tempo_preparo // 60
                minutos = tempo_preparo % 60
                tempo_preparo = f"{horas:02}:{minutos:02}:00"
            except ValueError:
                raise ValidationError({"tempo_preparo": "O tempo de preparo deve ser um número inteiro representando minutos."})

        # Construção do filtro dinâmico
        filtros = Q()
        if tipo:
            filtros &= Q(tipo__iexact=tipo)  # Combina com AND lógico
        if restricoes_alimentares:
            restricoes_query = Q()
            for restricao in restricoes_alimentares:
                restricoes_query |= Q(restricao_alimentar__icontains=restricao)  # Combina com OR lógico
            filtros &= restricoes_query  # Adiciona ao filtro principal com AND lógico
        if dificuldade:
            filtros &= Q(dificuldade__iexact=dificuldade)
        if categoria:
            filtros &= Q(categoria=categoria)  # Filtro por categoria
        if tempo_preparo:
            try:
                horas, minutos, _ = map(int, tempo_preparo.split(':'))
                tempo_preparo_minutos = horas * 60 + minutos
                if tempo_preparo_minutos == 20:
                    filtros &= Q(tempo_preparo__lte="00:20:00")
                elif tempo_preparo_minutos == 30:
                    filtros &= Q(tempo_preparo__gt="00:20:00", tempo_preparo__lte="00:30:00")
                elif tempo_preparo_minutos == 40:
                    filtros &= Q(tempo_preparo__gt="00:30:00", tempo_preparo__lte="00:40:00")
                elif tempo_preparo_minutos == 60:
                    filtros &= Q(tempo_preparo__gt="00:40:00", tempo_preparo__lte="01:00:00")
                elif tempo_preparo_minutos > 60:
                    filtros &= Q(tempo_preparo__gt="01:00:00")
            except ValueError:
                raise ValidationError({"tempo_preparo": "O tempo de preparo deve ser um número inteiro representando minutos."})
        if ingredientes:
            ingredientes_query = Q()
            for ingrediente in ingredientes:
                ingredientes_query |= Q(ingredientes__id_ingrediente__nome__icontains=ingrediente)  # Combina com OR lógico
            filtros &= ingredientes_query  # Adiciona ao filtro principal com AND lógico
        if search:
            filtros &= Q(titulo__icontains=search)  # Busca no título da receita

        # Log para depuração
        print(f"Ingredientes recebidos: {ingredientes}")
        print(f"Filtros aplicados: {filtros}")

        # Consulta ao banco de dados
        try:
            receitas = Receita.objects.filter(filtros).select_related('id_usuario').distinct()
        except Exception as e:
            raise ValidationError({"error": f"Erro ao consultar receitas: {str(e)}"})

        if not receitas.exists():
            return Response({"message": "Nenhuma receita encontrada com os filtros fornecidos."}, status=404)

        serializer = ReceitaSerializer(receitas, many=True)
        return Response(serializer.data)

class ReceitaMaisAcessadasAPIView(APIView):
    """
    Endpoint para listar as receitas mais acessadas.
    """
    def get(self, request):
        try:
            receitas = Receita.objects.all().order_by('-quantidade_visualizacao')
            serializer = ReceitaSerializer(receitas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": f"Erro ao buscar receitas mais acessadas: {str(e)}"}, status=500)

class ReceitaAleatoriaAPIView(APIView):
    """
    Endpoint para listar receitas aleatórias.
    """
    def get(self, request):
        try:
            receitas = list(Receita.objects.all())
            random_receitas = sample(receitas, min(len(receitas), 10))  # Seleciona até 10 receitas aleatórias
            serializer = ReceitaSerializer(random_receitas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": f"Erro ao buscar receitas aleatórias: {str(e)}"}, status=500)

@extend_schema(
    tags=['receitas'],
    summary="Listar todas as categorias de receitas",
    description="Retorna todas as categorias disponíveis para receitas com estatísticas de uso.",
    responses={
        200: OpenApiResponse(
            description="Lista de categorias com estatísticas"
        )
    }
)
class ReceitaCategoriasAPIView(APIView):
    """
    Endpoint para listar todas as categorias disponíveis para receitas.
    """
    def get(self, request):
        try:
            categorias = [
                {"codigo": codigo, "nome": nome} 
                for codigo, nome in Receita.CATEGORIA_CHOICES
            ]
            
            # Estatísticas por categoria (opcional)
            estatisticas = []
            for codigo, nome in Receita.CATEGORIA_CHOICES:
                count = Receita.objects.filter(categoria=codigo).count()
                estatisticas.append({
                    "codigo": codigo,
                    "nome": nome,
                    "quantidade_receitas": count
                })
            
            return Response({
                "categorias": categorias,
                "total_categorias": len(categorias),
                "estatisticas_por_categoria": estatisticas
            })
        except Exception as e:
            return Response({"error": f"Erro ao buscar categorias: {str(e)}"}, status=500)

@extend_schema(
    tags=['receitas'],
    summary="Listar receitas por categoria",
    description="Retorna todas as receitas de uma categoria específica.",
    parameters=[
        OpenApiParameter(
            name='categoria',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Código da categoria (ex: massas, carnes, sobremesas)'
        )
    ],
    responses={
        200: OpenApiResponse(
            description="Receitas da categoria especificada"
        ),
        404: OpenApiResponse(description="Categoria não encontrada ou sem receitas")
    }
)
class ReceitaPorCategoriaAPIView(APIView):
    """
    Endpoint para listar receitas de uma categoria específica.
    """
    def get(self, request, categoria):
        try:
            # Valida se a categoria existe
            valid_categorias = [choice[0] for choice in Receita.CATEGORIA_CHOICES]
            if categoria not in valid_categorias:
                return Response(
                    {"error": f"Categoria '{categoria}' não encontrada. Categorias válidas: {', '.join(valid_categorias)}"},
                    status=404
                )
            
            # Busca receitas da categoria
            receitas = Receita.objects.filter(categoria=categoria).select_related('id_usuario')
            
            if not receitas.exists():
                categoria_nome = dict(Receita.CATEGORIA_CHOICES).get(categoria, categoria)
                return Response({
                    "message": f"Nenhuma receita encontrada na categoria '{categoria_nome}'.",
                    "categoria": {"codigo": categoria, "nome": categoria_nome},
                    "total_receitas": 0,
                    "receitas": []
                })
            
            serializer = ReceitaSerializer(receitas, many=True)
            categoria_nome = dict(Receita.CATEGORIA_CHOICES).get(categoria, categoria)
            
            return Response({
                "categoria": {"codigo": categoria, "nome": categoria_nome},
                "total_receitas": receitas.count(),
                "receitas": serializer.data
            })
            
        except Exception as e:
            return Response({"error": f"Erro ao buscar receitas da categoria: {str(e)}"}, status=500)

# Views para a API de ReceitaIngrediente
class ReceitaIngredienteListCreateAPIView(generics.ListCreateAPIView):
    queryset = ReceitaIngrediente.objects.all()
    serializer_class = ReceitaIngredienteSerializer

class ReceitaIngredienteRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReceitaIngrediente.objects.all()
    serializer_class = ReceitaIngredienteSerializer
    def get_object(self):
        try:
            return ReceitaIngrediente.objects.get(pk=self.kwargs['pk'])
        except ReceitaIngrediente.DoesNotExist:
            raise NotFound(detail="ReceitaIngrediente não encontrado.")
        except Exception as e:
            raise NotFound(detail=f"Erro inesperado: {str(e)}")
