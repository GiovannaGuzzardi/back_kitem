from django.urls import path
from . import views_api  # Importa as views do arquivo views_api.py
from rest_framework.routers import DefaultRouter
from .views import FavoritoViewSet

router = DefaultRouter()
router.register(r'favoritos', FavoritoViewSet)

urlpatterns = [
    # API Root (opcional)
    path('', views_api.api_root, name='favorito-api-root'),

    # URLs para Favoritos
    path('favoritos/', views_api.FavoritoListCreateAPIView.as_view(), name='favorito-list-create'),
    path('favoritos/<int:pk>/', views_api.FavoritoRetrieveUpdateDestroyAPIView.as_view(), name='favorito-detail'),
    
    # URL para obter receitas favoritas de um usuário específico
    path('usuarios/<int:id_usuario>/favoritos/', views_api.ReceitasFavoritasAPIView.as_view(), name='receitas-favoritas'),
] + router.urls
