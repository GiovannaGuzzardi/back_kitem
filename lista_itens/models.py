from django.db import models
from django.contrib.auth.models import User as Usuario
from ingrediente.models import Ingrediente

class ListaItens(models.Model):
    id = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='listas_itens')

    def __str__(self):
        return f"Lista de {self.id_usuario.username}"

    class Meta:
        verbose_name = 'Lista de itens faltantes'
        verbose_name_plural = 'Listas de itens faltantes'


class ListaItensIngrediente(models.Model):
    id = models.AutoField(primary_key=True)
    id_ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name='listas_itens')
    id_lista = models.ForeignKey(ListaItens, on_delete=models.CASCADE, related_name='ingredientes')
    quantidade = models.FloatField(null=False)
    unidade_medida = models.CharField(max_length=25, null=False)
    preco = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.id_lista} - {self.id_ingrediente.nome}"

    class Meta:
        verbose_name = 'Item da Lista de Itens'
        verbose_name_plural = 'Itens da Lista de Itens'
        unique_together = ['id_lista', 'id_ingrediente']
