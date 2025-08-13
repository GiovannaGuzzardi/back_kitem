from rest_framework import viewsets
from rest_framework.response import Response
from .models import ListaItens, ListaItensIngrediente
from .serializers import ListaItensSerializer, ListaItensIngredienteSerializer

class ListaItensViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD em listas de itens.
    """
    queryset = ListaItens.objects.all()
    serializer_class = ListaItensSerializer
    
    def destroy(self, request, *args, **kwargs):
        """
        Impede a exclusão de listas conforme regra de negócio.
        """
        return Response(
            {"error": "Listas de itens não podem ser excluídas. Apenas ingredientes podem ser removidos."},
            status=405  # Method Not Allowed
        )


class ListaItensIngredienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD completas em ingredientes das listas.
    """
    queryset = ListaItensIngrediente.objects.all()
    serializer_class = ListaItensIngredienteSerializer
