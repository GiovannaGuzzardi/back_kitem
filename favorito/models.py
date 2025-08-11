from django.db import models
from django.contrib.auth.models import User as Usuario
from receita.models import Receita

class Favorito(models.Model):
    id = models.AutoField(primary_key=True)
    id_receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name='favoritos')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='favoritos')

    def __str__(self):
        return f"{self.id_usuario.username} - {self.id_receita.titulo}"

    class Meta:
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        unique_together = ['id_receita', 'id_usuario']
