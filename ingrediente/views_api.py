from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Ingrediente
from kiItem.serializers import IngredienteSerializer

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint para ingredientes
    """
    return Response({
        'ingredientes': request.build_absolute_uri('/api/ingredientes/'),
    })

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
