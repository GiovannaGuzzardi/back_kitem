from django.db import models
# pq importar user? pq o django ja tem um user padrao, e se eu quiser usar ele, eu preciso importar
# e fazer referencia a ele, caso contrario, eu teria que criar um user do zero, o que seria mais trabalhoso
from django.contrib.auth.models import User as Usuario
from ingrediente.models import Ingrediente

class Receita(models.Model):
    id = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='receitas')
    titulo = models.CharField(max_length=50, null=False)
    descricao = models.CharField(max_length=1500, null=False)
    tempo_preparo = models.TimeField(null=False)
    dificuldade = models.CharField(max_length=25, null=False)
    tipo = models.CharField(max_length=25, null=True)
    restricao_alimentar = models.CharField(max_length=25, null=True)
    imagem = models.URLField(max_length=600, null=True)
    quantidade_visualizacao = models.IntegerField(default=0, null=False)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'


class ReceitaIngrediente(models.Model):
    id = models.AutoField(primary_key=True)
    id_ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name='receitas')
    id_receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name='ingredientes')
    quantidade = models.FloatField(null=False)
    unidade_medida = models.CharField(max_length=25, null=False)

    def __str__(self):
        return f"{self.id_receita.titulo} - {self.id_ingrediente.nome}"

    class Meta:
        verbose_name = 'Receita Ingrediente'
        verbose_name_plural = 'Receitas Ingredientes'
        unique_together = ['id_receita', 'id_ingrediente']
