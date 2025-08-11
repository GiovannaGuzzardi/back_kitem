"""
URL configuration for kiItem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views_api  # Importa as views do arquivo views_api.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views_api import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Root (opcional, pode ser removido se não for necessário)
    path('api/', views_api.api_root, name='api-root'),

    # rota de auth
    path('api/auth/login2/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # URLs para Usuários
    path('api/usuarios/', views_api.UsuarioListCreateAPIView.as_view(), name='usuario-list-create'),
    path('api/usuarios/<int:pk>/', views_api.UsuarioRetrieveUpdateDestroyAPIView.as_view(), name='usuario-detail'),

    # URLs dos apps
    path('api/', include('ingrediente.urls')),
    path('api/', include('receita.urls')),
    path('api/', include('favorito.urls')),
    path('api/', include('lista_itens.urls')),
]
