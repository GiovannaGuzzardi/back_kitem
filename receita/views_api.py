from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from random import sample
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
        # Validações
        valid_tipos = ["doce", "salgado"]
        valid_dificuldades = ["Fácil", "Média", "Difícil", "Master Chef"]
        valid_operadores = ["mais", "menos"]

        if tipo and tipo not in valid_tipos:
            raise ValidationError({"tipo": f"Tipo inválido. Valores permitidos: {', '.join(valid_tipos)}"})

        if dificuldade and dificuldade not in valid_dificuldades:
            raise ValidationError({"dificuldade": f"Dificuldade inválida. Valores permitidos: {', '.join(valid_dificuldades)}"})

        if tempo_preparo_operador and tempo_preparo_operador not in valid_operadores:
            raise ValidationError({"tempo_preparo_operador": f"Operador inválido. Valores permitidos: {', '.join(valid_operadores)}"})

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
