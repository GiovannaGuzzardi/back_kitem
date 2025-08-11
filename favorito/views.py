from rest_framework import viewsets
from .models import Favorito
from .serializers import FavoritoSerializer

class FavoritoViewSet(viewsets.ModelViewSet):
    queryset = Favorito.objects.all()
    serializer_class = FavoritoSerializer
