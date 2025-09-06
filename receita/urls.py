from django.urls import path
from . import views_api  # Importa as views do arquivo views_api.py
from rest_framework.routers import DefaultRouter
from .views import ReceitaViewSet, ReceitaIngredienteViewSet

router = DefaultRouter()
router.register(r'receitas', ReceitaViewSet)
router.register(r'receita-ingredientes', ReceitaIngredienteViewSet)

urlpatterns = [
    # API Root (opcional)
    path('', views_api.api_root, name='receita-api-root'),

    # URLs para Receitas
    path('receitas/', views_api.ReceitaListCreateAPIView.as_view(), name='receita-list-create'),
    path('receitas/<int:pk>/', views_api.ReceitaRetrieveUpdateDestroyAPIView.as_view(), name='receita-detail'),
    # URL para receitas por usuário
    path('receitas/usuario/<int:user_id>/', views_api.GetReceitaUsuario.as_view(), name='receitas-por-usuario'),
    # URL para Receita Detalhada
    path('receitas/<int:pk>/detalhada/', views_api.ReceitaDetalhadaAPIView.as_view(), name='receita-detalhada'),
    # URL para filtro de receitas
    path('receitas/filtrar/', views_api.ReceitaFilterAPIView.as_view(), name='receita-filtrar'),
    # URL para receitas mais acessadas
    path('receitas/mais-acessadas/', views_api.ReceitaMaisAcessadasAPIView.as_view(), name='receitas-mais-acessadas'),
    # URL para receitas aleatórias
    path('receitas/aleatorias/', views_api.ReceitaAleatoriaAPIView.as_view(), name='receitas-aleatorias'),

    # URLs para categorias de receitas
    path('receitas/categorias/', views_api.ReceitaCategoriasAPIView.as_view(), name='receita-categorias'),
    path('receitas/categoria/<str:categoria>/', views_api.ReceitaPorCategoriaAPIView.as_view(), name='receitas-por-categoria'),

    # URLs para ReceitaIngrediente
    path('receita_ingredientes/', views_api.ReceitaIngredienteListCreateAPIView.as_view(), name='receita-ingrediente-list-create'),
    path('receita_ingredientes/<int:pk>/', views_api.ReceitaIngredienteRetrieveUpdateDestroyAPIView.as_view(), name='receita-ingrediente-detail'),
] + router.urls
