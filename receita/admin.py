from django.contrib import admin
from .models import Receita, ReceitaIngrediente

class ReceitaIngredienteInline(admin.TabularInline):
    model = ReceitaIngrediente
    extra = 1

@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'id_usuario', 'tempo_preparo', 'dificuldade', 'quantidade_visualizacao']
    list_filter = ['dificuldade', 'tipo', 'restricao_alimentar']
    search_fields = ['titulo', 'descricao']
    inlines = [ReceitaIngredienteInline]

@admin.register(ReceitaIngrediente)
class ReceitaIngredienteAdmin(admin.ModelAdmin):
    list_display = ['id_receita', 'id_ingrediente', 'quantidade', 'unidade_medida']
    list_filter = ['id_receita', 'id_ingrediente']
