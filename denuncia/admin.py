from django.contrib import admin
from .models import Denuncia

@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = [
        'unique_id', 
        'get_receita_titulo', 
        'get_motivo_display', 
        'get_denunciante_username', 
        'data_denuncia'
    ]
    list_filter = [
        'motivo_denuncia', 
        'data_denuncia', 
        'id_receita__tipo'
    ]
    search_fields = [
        'id_receita__titulo', 
        'id_denunciante__username', 
        'detalhamento'
    ]
    readonly_fields = ['unique_id', 'data_denuncia']
    ordering = ['-data_denuncia']
    
    fieldsets = (
        ('Informações da Denúncia', {
            'fields': ('unique_id', 'data_denuncia')
        }),
        ('Detalhes', {
            'fields': ('id_receita', 'motivo_denuncia', 'detalhamento')
        }),
        ('Denunciante', {
            'fields': ('id_denunciante',)
        }),
    )
    
    def get_receita_titulo(self, obj):
        return obj.id_receita.titulo
    get_receita_titulo.short_description = 'Receita'
    get_receita_titulo.admin_order_field = 'id_receita__titulo'
    
    def get_motivo_display(self, obj):
        return obj.get_motivo_denuncia_display()
    get_motivo_display.short_description = 'Motivo'
    get_motivo_display.admin_order_field = 'motivo_denuncia'
    
    def get_denunciante_username(self, obj):
        return obj.id_denunciante.username
    get_denunciante_username.short_description = 'Denunciante'
    get_denunciante_username.admin_order_field = 'id_denunciante__username'
    
    # Ações customizadas para o admin
    actions = ['marcar_como_resolvida']
    
    def marcar_como_resolvida(self, request, queryset):
        # Ação futura para marcar denúncias como resolvidas
        # Por enquanto, apenas uma mensagem
        self.message_user(request, f"{queryset.count()} denúncias selecionadas. Funcionalidade de resolução será implementada futuramente.")
    marcar_como_resolvida.short_description = "Marcar denúncias selecionadas como resolvidas"
