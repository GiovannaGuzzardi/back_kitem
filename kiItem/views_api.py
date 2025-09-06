from rest_framework import generics
from ingrediente.models import Ingrediente
from receita.models import Receita, ReceitaIngrediente
from favorito.models import Favorito
from lista_itens.models import ListaItens as ListaCompras, ListaItensIngrediente as ListaComprasIngrediente
from denuncia.models import Denuncia
from .serializers import (
    CustomTokenObtainPairSerializer,
    IngredienteSerializer,
    ReceitaSerializer,
    ReceitaIngredienteSerializer,
    FavoritoSerializer,
    ListaComprasSerializer,
    ListaComprasIngredienteSerializer,
    UsuarioSerializer,
    DenunciaSerializer,
)
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User as Usuario
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from datetime import timedelta
from random import sample
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UsuarioListCreateAPIView(generics.ListCreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class UsuarioRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_object(self):
        try:
            return Usuario.objects.get(pk=self.kwargs['pk'])
        except Usuario.DoesNotExist:
            raise NotFound(detail="Usuário não encontrado.")
        except Exception as e:
            raise NotFound(detail=f"Erro inesperado: {str(e)}")

# Views para a API de Ingredientes
class IngredienteListCreateAPIView(generics.ListCreateAPIView):
    queryset = Ingrediente.objects.all()
    serializer_class = IngredienteSerializer

# Adição de um método get_object para lidar com a busca de um objeto específico
class IngredienteRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ingrediente.objects.all()
    serializer_class = IngredienteSerializer
    def get_object(self):
        # tenta buscar o objeto
        try:
            # self.kwargs é um dicionário que contém os parâmetros da URL 
            return Ingrediente.objects.get(pk=self.kwargs['pk'])
        except Ingrediente.DoesNotExist:
            raise NotFound(detail="Ingrediente não encontrado.")
        except Exception as e:
            raise NotFound(detail=f"Erro inesperado: {str(e)}")

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
    Endpoint para filtrar receitas com base em tipo, categoria, restrição alimentar, dificuldade, tempo de preparo e pesquisa por nome.
    """
    def get(self, request):
        tipo = request.query_params.get('tipo')
        categoria = request.query_params.get('categoria')  # Novo filtro por categoria
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
        valid_categorias = [choice[0] for choice in Receita.CATEGORIA_CHOICES]

        if tipo and tipo not in valid_tipos:
            raise ValidationError({"tipo": f"Tipo inválido. Valores permitidos: {', '.join(valid_tipos)}"})

        if categoria and categoria not in valid_categorias:
            raise ValidationError({"categoria": f"Categoria inválida. Valores permitidos: {', '.join(valid_categorias)}"})

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
        if categoria:
            filtros &= Q(categoria__iexact=categoria)  # Filtro por categoria
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

class ReceitasFavoritasAPIView(APIView):
    def get(self, request, id_usuario):
        try:
            # Filtra os favoritos pelo id_usuario
            favoritos = Favorito.objects.filter(id_usuario=id_usuario).select_related('id_receita')
            
            if not favoritos.exists():
                return Response({"message": "Nenhuma receita favorita encontrada para este usuário."}, status=404)

            # Obtém as receitas favoritas
            receitas = [favorito.id_receita for favorito in favoritos]
            serializer = ReceitaSerializer(receitas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": f"Erro ao buscar receitas favoritas: {str(e)}"}, status=500)

# Views para a API de Lista de Compras
class ListaComprasListCreateAPIView(generics.ListCreateAPIView):
    queryset = ListaCompras.objects.all()
    serializer_class = ListaComprasSerializer

class ListaComprasRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ListaCompras.objects.all()
    serializer_class = ListaComprasSerializer
    def get_object(self):
        try:
            return ListaCompras.objects.get(pk=self.kwargs['pk'])
        except ListaCompras.DoesNotExist:
            raise NotFound(detail="Lista de Compras não encontrada.")
        except Exception as e:
            raise NotFound(detail=f"Erro inesperado: {str(e)}")

# Views para a API de ListaComprasIngrediente
class ListaComprasIngredienteListCreateAPIView(generics.ListCreateAPIView):
    queryset = ListaComprasIngrediente.objects.all()
    serializer_class = ListaComprasIngredienteSerializer

class ListaComprasIngredienteRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ListaComprasIngrediente.objects.all()
    serializer_class = ListaComprasIngredienteSerializer
    def get_object(self):
        try:
            return ListaComprasIngrediente.objects.get(pk=self.kwargs['pk'])
        except ListaComprasIngrediente.DoesNotExist:
            raise NotFound(detail="Ingrediente da Lista de Compras não encontrado.")
        except Exception as e:
            raise NotFound(detail=f"Erro inesperado: {str(e)}")


@api_view(['GET'])
def api_root(request):
    return Response({
        "message": "Seja bem-vindo à API de testes do kitem",
        "endpoints": {
            "auth": "/auth/login/",
            "refresh": "/auth/refresh/",
            "usuarios": "/usuarios/",
            "usuario": "/usuarios/<int:pk>/",
            "usuarios_favoritos": "/usuarios/<int:id_usuario>/favoritos/",
            "usuarios_favorito_delete": "/usuarios/<int:id_usuario>/favoritos/<int:receita_id>/ [RECOMENDADO]",
            "ingredientes": "/ingredientes/",
            "ingrediente": "/ingredientes/<int:pk>/",
            "receitas": "/receitas/",
            "receita": "/receitas/<int:pk>/",
            "receitas_usuario": "/receitas/usuario/<int:user_id>/",
            "receita_detalhada": "/receitas/<int:pk>/detalhada/",
            "receitas_filtrar": "/receitas/filtrar/",
            "receitas_mais_acessadas": "/receitas/mais-acessadas/",
            "receitas_aleatorias": "/receitas/aleatorias/",
            "receita_ingredientes": "/receita_ingredientes/",
            "receita_ingrediente": "/receita_ingredientes/<int:pk>/",
            "favoritos": "/favoritos/",
            "favorito": "/favoritos/<int:pk>/",
            "lista_itens": "/lista_itens/",
            "lista_item": "/lista_itens/<int:pk>/",
            "lista_itens_ingredientes": "/lista_itens_ingredientes/",
            "lista_itens_ingrediente": "/lista_itens_ingredientes/<int:pk>/",
            "denuncias": "/denuncias/lista/",
            "denuncia": "/denuncias/<uuid:unique_id>/",
            "denuncias_por_receita": "/denuncias/receita/<int:receita_id>/",
            "denuncias_por_usuario": "/denuncias/usuario/<int:usuario_id>/",
            "denuncias_filtrar": "/denuncias/filtrar/",
            "denuncias_estatisticas": "/denuncias/estatisticas/",
            "listas_compras": "/listas_compras/ [DEPRECADO]",
            "lista_compras": "/listas_compras/<int:pk>/ [DEPRECADO]",
            "listas_compras_ingredientes": "/listas_compras_ingredientes/ [DEPRECADO]",
            "lista_compras_ingrediente": "/listas_compras_ingredientes/<int:pk>/ [DEPRECADO]",
        },
        "aviso_importante": {
            "deprecacao": "Os endpoints com nomenclatura 'lista_compras' estão DEPRECADOS.",
            "status": "Ainda funcionam normalmente na versão atual, mas serão removidos em futuras atualizações.",
            "recomendacao": "Migre para os novos endpoints 'lista_itens' o mais rápido possível.",
            "motivo": "Padronização da nomenclatura da API para melhor organização e clareza."
        },
        "seguranca_favoritos": {
            "endpoint_recomendado": "DELETE /usuarios/<id_usuario>/favoritos/<receita_id>/",
            "motivo": "Garante que o usuário só pode deletar seus próprios favoritos",
            "endpoint_legado": "DELETE /favoritos/<pk>/",
            "aviso": "Endpoint legado ainda funciona, mas use o recomendado para maior segurança"
        },
        "swagger_documentation": {
            "schema": "/api/schema/",
            "swagger_ui": "/api/docs/",
            "redoc": "/api/redoc/",
            "descricao": "Documentação interativa da API com Swagger/OpenAPI"
        },
        "denuncias": {
            "denuncias": "/api/denuncias/",
            "denuncias_lista": "/api/denuncias/lista/",
            "denuncia_detail": "/api/denuncias/<uuid>/",
            "denuncias_por_receita": "/api/denuncias/receita/<receita_id>/",
            "denuncias_por_usuario": "/api/denuncias/usuario/<usuario_id>/",
            "filtrar_denuncias": "/api/denuncias/filtrar/",
            "estatisticas_denuncias": "/api/denuncias/estatisticas/",
            "descricao": "Sistema completo de denúncias de receitas"
        }
    })

# Views para a API de Denúncias
class DenunciaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Denuncia.objects.all()
    serializer_class = DenunciaSerializer

class DenunciaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Denuncia.objects.all()
    serializer_class = DenunciaSerializer
    lookup_field = 'unique_id'
    
    def get_object(self):
        try:
            return Denuncia.objects.get(unique_id=self.kwargs['unique_id'])
        except Denuncia.DoesNotExist:
            raise NotFound(detail="Denúncia não encontrada.")
        except Exception as e:
            raise NotFound(detail=f"Erro inesperado: {str(e)}")

@api_view(['GET'])
def root(request):
    return Response({
        "message": "Seja bem-vindo à nossa aplicação",
        "Base de prod(atualmente indisponível)": "/api2/",
        "Base de dev": "/api/",
    })
