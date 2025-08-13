from django.urls import path
from . import views_api  # Importa as views do arquivo views_api.py
from rest_framework.routers import DefaultRouter
from .views import FavoritoViewSet

router = DefaultRouter()
router.register(r'favoritos', FavoritoViewSet)

urlpatterns = [
    # API Root (opcional)
    path('', views_api.api_root, name='favorito-api-root'),

    # URLs para Favoritos - CRUD básico
    path('favoritos/', views_api.FavoritoListCreateAPIView.as_view(), name='favorito-list-create'),
    path('favoritos/<int:pk>/', views_api.FavoritoRetrieveUpdateDestroyAPIView.as_view(), name='favorito-detail'),
    
    # URLs para operações específicas por usuário
    path('usuarios/<int:user_id>/favoritos/', views_api.GetFavoritoUsuario.as_view(), name='get-favorito-usuario'),
    path('usuarios/<int:user_id>/favoritos/detalhados/', views_api.FavoritoDetalhadoAPIView.as_view(), name='favorito-detalhado'),
    path('usuarios/<int:user_id>/favoritos/filtrar/', views_api.FavoritoFilterAPIView.as_view(), name='favorito-filter'),
    
    # URLs para operações de toggle e delete
    path('usuarios/<int:user_id>/favoritos/<int:receita_id>/toggle/', views_api.FavoritoToggleAPIView.as_view(), name='favorito-toggle'),
    path('usuarios/<int:user_id>/favoritos/<int:receita_id>/', views_api.FavoritoDeleteByUsuarioReceitaAPIView.as_view(), name='favorito-delete-by-usuario-receita'),
    
    # URL para compatibilidade (mantida para não quebrar APIs existentes)
    path('usuarios/<int:id_usuario>/favoritos/', views_api.ReceitasFavoritasAPIView.as_view(), name='receitas-favoritas'),
] + router.urls
