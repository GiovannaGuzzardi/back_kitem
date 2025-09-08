from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Receita, ReceitaIngrediente
from .serializers import ReceitaSerializer, ReceitaIngredienteSerializer

class ReceitaViewSet(viewsets.ModelViewSet):
    queryset = Receita.objects.all()
    serializer_class = ReceitaSerializer

    @action(detail=True, methods=['post'])
    def adicionar_ingrediente(self, request, pk=None):
        """Adiciona um ingrediente a uma receita"""
        receita = self.get_object()
        serializer = ReceitaIngredienteSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(id_receita=receita)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def ingredientes(self, request, pk=None):
        """Lista todos os ingredientes de uma receita"""
        receita = self.get_object()
        ingredientes = ReceitaIngrediente.objects.filter(id_receita=receita)
        serializer = ReceitaIngredienteSerializer(ingredientes, many=True)
        return Response(serializer.data)


class ReceitaIngredienteViewSet(viewsets.ModelViewSet):
    queryset = ReceitaIngrediente.objects.all()
    serializer_class = ReceitaIngredienteSerializer

from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError

def health_check(request):
    try:
        # Tenta fazer a consulta mais simples possível ao banco de dados
        connection.cursor()
        return JsonResponse({"status": "ok", "message": "Conexão com o banco de dados bem-sucedida!"})
    except OperationalError as e:
        # Se falhar, retorna o erro exato
        return JsonResponse({"status": "error", "message": f"Não foi possível conectar ao banco de dados: {str(e)}"}, status=500)
    except Exception as e:
        # Pega qualquer outro erro inesperado
        return JsonResponse({"status": "error", "message": f"Ocorreu um erro inesperado: {str(e)}"}, status=500)
