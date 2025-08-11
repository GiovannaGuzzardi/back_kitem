from django.urls import path
from . import views_api  # Importa as views do arquivo views_api.py
from rest_framework import routers
from .views import IngredienteViewSet

router = routers.DefaultRouter()
router.register(r'ingredientes', IngredienteViewSet)

urlpatterns = [
    # API Root (opcional)
    path('', views_api.api_root, name='ingrediente-api-root'),

    # URLs para Ingredientes
    path('ingredientes/', views_api.IngredienteListCreateAPIView.as_view(), name='ingrediente-list-create'),
    path('ingredientes/<int:pk>/', views_api.IngredienteRetrieveUpdateDestroyAPIView.as_view(), name='ingrediente-detail'),
] + router.urls