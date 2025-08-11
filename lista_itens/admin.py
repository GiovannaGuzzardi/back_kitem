from django.contrib import admin
from .models import ListaItens, ListaItensIngrediente

class ListaItensIngredienteInline(admin.TabularInline):
    model = ListaItensIngrediente
    extra = 1

@admin.register(ListaItens)
class ListaItensAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_usuario']
    list_filter = ['id_usuario']
    search_fields = ['id_usuario__username']
    inlines = [ListaItensIngredienteInline]

@admin.register(ListaItensIngrediente)
class ListaItensIngredienteAdmin(admin.ModelAdmin):
    list_display = ['id_lista', 'id_ingrediente', 'quantidade', 'unidade_medida', 'preco']
    list_filter = ['id_lista', 'id_ingrediente']
    search_fields = ['id_ingrediente__nome']
