from rest_framework import viewsets
from .models import ListaItens, ListaItensIngrediente
from .serializers import ListaItensSerializer, ListaItensIngredienteSerializer

class ListaItensViewSet(viewsets.ModelViewSet):
    queryset = ListaItens.objects.all()
    serializer_class = ListaItensSerializer


class ListaItensIngredienteViewSet(viewsets.ModelViewSet):
    queryset = ListaItensIngrediente.objects.all()
    serializer_class = ListaItensIngredienteSerializer
