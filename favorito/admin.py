from django.contrib import admin
from .models import Favorito

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ['id_usuario', 'id_receita']
    list_filter = ['id_usuario', 'id_receita']
    search_fields = ['id_usuario__username', 'id_receita__titulo']
