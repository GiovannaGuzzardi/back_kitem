from django.urls import path
from . import views_api  # Importa as views do arquivo views_api.py
from rest_framework.routers import DefaultRouter
from .views import DenunciaViewSet

# Usando router para ViewSets (opcional)
router = DefaultRouter()
router.register(r'denuncias', DenunciaViewSet, basename='denuncia')

urlpatterns = [
    # API Root (opcional)
    path('denuncias/', views_api.api_root, name='denuncia-api-root'),

    # URLs para Denúncias
    path('denuncias/lista/', views_api.DenunciaListCreateAPIView.as_view(), name='denuncia-list-create'),
    path('denuncias/<uuid:unique_id>/', views_api.DenunciaRetrieveUpdateDestroyAPIView.as_view(), name='denuncia-detail'),

    # URLs para filtros e buscas específicas
    path('denuncias/receita/<int:receita_id>/', views_api.DenunciasPorReceitaAPIView.as_view(), name='denuncias-por-receita'),
    path('denuncias/usuario/<int:usuario_id>/', views_api.DenunciasPorUsuarioAPIView.as_view(), name='denuncias-por-usuario'),
    
    # URLs para filtros avançados e estatísticas
    path('denuncias/filtrar/', views_api.DenunciaFilterAPIView.as_view(), name='denuncias-filtrar'),
    path('denuncias/estatisticas/', views_api.DenunciaEstatisticasAPIView.as_view(), name='denuncias-estatisticas'),
    
    # URL para futuras funcionalidades de moderação
    path('denuncias/<uuid:unique_id>/toggle-status/', views_api.DenunciaToggleStatusAPIView.as_view(), name='denuncia-toggle-status'),
] + router.urls
