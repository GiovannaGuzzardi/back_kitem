from django.urls import path
from . import views_api  # Importa as views do arquivo views_api.py
from rest_framework.routers import DefaultRouter
from .views import ListaItensViewSet, ListaItensIngredienteViewSet

# Usando router para ViewSets (opcional)
router = DefaultRouter()
router.register(r'listas-itens', ListaItensViewSet)
router.register(r'lista-itens-ingredientes', ListaItensIngredienteViewSet)

urlpatterns = [
    # API Root (opcional)
    path('', views_api.api_root, name='lista-itens-api-root'),

    # URLs para Lista de Itens (novo nome)
    path('listas_itens/', views_api.ListaItensListCreateAPIView.as_view(), name='lista-itens-list-create'),
    path('listas_itens/<int:pk>/', views_api.ListaItensRetrieveUpdateDestroyAPIView.as_view(), name='lista-itens-detail'),

    # URLs para ListaItensIngrediente (novo nome)
    path('listas_itens_ingredientes/', views_api.ListaItensIngredienteListCreateAPIView.as_view(), name='lista-itens-ingrediente-list-create'),
    path('listas_itens_ingredientes/<int:pk>/', views_api.ListaItensIngredienteRetrieveUpdateDestroyAPIView.as_view(), name='lista-itens-ingrediente-detail'),

    # URLs para Lista de Compras (compatibilidade com nome antigo)
    path('listas_compras/', views_api.ListaComprasListCreateAPIView.as_view(), name='lista-compras-list-create'),
    path('listas_compras/<int:pk>/', views_api.ListaComprasRetrieveUpdateDestroyAPIView.as_view(), name='lista-compras-detail'),

    # URLs para ListaComprasIngrediente (compatibilidade com nome antigo)
    path('listas_compras_ingredientes/', views_api.ListaComprasIngredienteListCreateAPIView.as_view(), name='lista-compras-ingrediente-list-create'),
    path('listas_compras_ingredientes/<int:pk>/', views_api.ListaComprasIngredienteRetrieveUpdateDestroyAPIView.as_view(), name='lista-compras-ingrediente-detail'),
] + router.urls
