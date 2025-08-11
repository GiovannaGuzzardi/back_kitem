from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from .models import ListaItens, ListaItensIngrediente
from kiItem.serializers import ListaItensSerializer, ListaItensIngredienteSerializer

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint para listas de itens
    """
    return Response({
        'lista_itens': request.build_absolute_uri('/api/lista_itens/'),
        'lista_itens_ingredientes': request.build_absolute_uri('/api/lista_itens_ingredientes/'),
        # Mantendo compatibilidade com nomes antigos
        'listas_compras': request.build_absolute_uri('/api/listas_compras/'),
        'listas_compras_ingredientes': request.build_absolute_uri('/api/listas_compras_ingredientes/'),
    })

# Views para a API de Lista Itens
class ListaItensListCreateAPIView(generics.ListCreateAPIView):
    queryset = ListaItens.objects.all()
    serializer_class = ListaItensSerializer

class ListaItensRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ListaItens.objects.all()
    serializer_class = ListaItensSerializer
    def get_object(self):
        try:
            return ListaItens.objects.get(pk=self.kwargs['pk'])
        except ListaItens.DoesNotExist:
            raise NotFound(detail="Lista de itens não encontrada.")
        except Exception as e:
            raise NotFound(detail=f"Erro inesperado: {str(e)}")

class GetListaItensUsuario(generics.ListAPIView):
    serializer_class = ListaItensSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']  # Pega o valor <user_id> da URL
        return ListaItens.objects.filter(id_usuario=user_id)

class ListaItensDetalhadaAPIView(APIView):
    def get(self, request, pk):
        try:
            lista = ListaItens.objects.get(pk=pk)
            ingredientes = ListaItensIngrediente.objects.filter(id_lista_itens=lista).select_related('id_ingrediente')

            data = {
                "id_lista": lista.id,
                "nome": lista.nome,
                "data_criacao": lista.data_criacao,
                "id_usuario": lista.id_usuario.id if lista.id_usuario else None,
                "ingredientes": [
                    {
                        "id_lista_ingrediente": ingrediente.id,
                        "quantidade": ingrediente.quantidade,
                        "unidade_medida": ingrediente.unidade_medida,
                        "nome_ingrediente": ingrediente.id_ingrediente.nome,
                        "comprado": ingrediente.comprado,
                    }
                    for ingrediente in ingredientes
                ],
                "total_ingredientes": ingredientes.count(),
                "ingredientes_comprados": ingredientes.filter(comprado=True).count(),
            }

            return Response(data)

        except ListaItens.DoesNotExist:
            raise NotFound(detail="Lista de itens não encontrada.")

class ListaItensFilterAPIView(APIView):
    """
    Endpoint para filtrar listas de itens com base em nome e status.
    """
    def get(self, request, user_id):
        nome = request.query_params.get('nome')
        status_compra = request.query_params.get('status')  # 'completa', 'incompleta', 'vazia'
        search = request.query_params.get('search')  # Campo de pesquisa para o nome da lista

        # Validações
        valid_status = ["completa", "incompleta", "vazia"]

        if status_compra and status_compra not in valid_status:
            raise ValidationError({"status": f"Status inválido. Valores permitidos: {', '.join(valid_status)}"})

        # Construção do filtro dinâmico
        filtros = Q(id_usuario=user_id)
        if nome:
            filtros &= Q(nome__icontains=nome)
        if search:
            filtros &= Q(nome__icontains=search)

        # Consulta ao banco de dados
        try:
            listas = ListaItens.objects.filter(filtros)
            
            # Filtro por status de compra
            if status_compra:
                listas_filtradas = []
                for lista in listas:
                    ingredientes = ListaItensIngrediente.objects.filter(id_lista_itens=lista)
                    total = ingredientes.count()
                    comprados = ingredientes.filter(comprado=True).count()
                    
                    if status_compra == 'completa' and total > 0 and comprados == total:
                        listas_filtradas.append(lista)
                    elif status_compra == 'incompleta' and total > 0 and comprados < total:
                        listas_filtradas.append(lista)
                    elif status_compra == 'vazia' and total == 0:
                        listas_filtradas.append(lista)
                
                listas = listas_filtradas
            
        except Exception as e:
            raise ValidationError({"error": f"Erro ao consultar listas: {str(e)}"})

        if not listas:
            return Response({"message": "Nenhuma lista encontrada com os filtros fornecidos."}, status=404)

        serializer = ListaItensSerializer(listas, many=True)
        return Response(serializer.data)

class ListaItensStatusAPIView(APIView):
    """
    Endpoint para obter estatísticas das listas de compras de um usuário.
    """
    def get(self, request, user_id):
        try:
            listas = ListaItens.objects.filter(id_usuario=user_id)
            
            total_listas = listas.count()
            listas_completas = 0
            listas_incompletas = 0
            listas_vazias = 0
            
            for lista in listas:
                ingredientes = ListaItensIngrediente.objects.filter(id_lista_itens=lista)
                total_ingredientes = ingredientes.count()
                ingredientes_comprados = ingredientes.filter(comprado=True).count()
                
                if total_ingredientes == 0:
                    listas_vazias += 1
                elif ingredientes_comprados == total_ingredientes:
                    listas_completas += 1
                else:
                    listas_incompletas += 1

            data = {
                "user_id": user_id,
                "total_listas": total_listas,
                "listas_completas": listas_completas,
                "listas_incompletas": listas_incompletas,
                "listas_vazias": listas_vazias,
            }

            return Response(data)

        except Exception as e:
            return Response({"error": f"Erro ao calcular estatísticas: {str(e)}"}, status=500)

# Views para a API de Lista Itens Ingrediente
class ListaItensIngredienteListCreateAPIView(generics.ListCreateAPIView):
    queryset = ListaItensIngrediente.objects.all()
    serializer_class = ListaItensIngredienteSerializer

class ListaItensIngredienteRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ListaItensIngrediente.objects.all()
    serializer_class = ListaItensIngredienteSerializer
    def get_object(self):
        try:
            return ListaItensIngrediente.objects.get(pk=self.kwargs['pk'])
        except ListaItensIngrediente.DoesNotExist:
            raise NotFound(detail="Lista Itens Ingrediente não encontrado.")
        except Exception as e:
            raise NotFound(detail=f"Erro inesperado: {str(e)}")

class ListaItensIngredienteToggleCompradoAPIView(APIView):
    """
    Endpoint para marcar/desmarcar um ingrediente como comprado.
    """
    def patch(self, request, pk):
        try:
            ingrediente = ListaItensIngrediente.objects.get(pk=pk)
            ingrediente.comprado = not ingrediente.comprado
            ingrediente.save()
            
            serializer = ListaItensIngredienteSerializer(ingrediente)
            return Response({
                "message": f"Ingrediente {'marcado como comprado' if ingrediente.comprado else 'desmarcado'}.",
                "ingrediente": serializer.data
            })
            
        except ListaItensIngrediente.DoesNotExist:
            raise NotFound(detail="Ingrediente não encontrado.")
        except Exception as e:
            return Response({"error": f"Erro ao atualizar ingrediente: {str(e)}"}, status=500)

# Views para compatibilidade com nomenclatura anterior (lista_compras)
class ListaComprasListCreateAPIView(ListaItensListCreateAPIView):
    """Alias para compatibilidade com API anterior"""
    pass

class ListaComprasRetrieveUpdateDestroyAPIView(ListaItensRetrieveUpdateDestroyAPIView):
    """Alias para compatibilidade com API anterior"""
    pass

class GetListaComprasUsuario(GetListaItensUsuario):
    """Alias para compatibilidade com API anterior"""
    pass

class ListaComprasIngredienteListCreateAPIView(ListaItensIngredienteListCreateAPIView):
    """Alias para compatibilidade com API anterior"""
    pass

class ListaComprasIngredienteRetrieveUpdateDestroyAPIView(ListaItensIngredienteRetrieveUpdateDestroyAPIView):
    """Alias para compatibilidade com API anterior"""
    pass
