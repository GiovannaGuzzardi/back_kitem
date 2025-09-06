from django.db import models
from django.contrib.auth.models import User
from receita.models import Receita
import uuid

class Denuncia(models.Model):
    # Motivos de denúncia como choices para melhor validação
    MOTIVO_CHOICES = [
        (1, 'Conteúdo inadequado'),
        (2, 'Spam'),
        (3, 'Informações falsas'),
        (4, 'Violação de direitos autorais'),
        (5, 'Conteúdo ofensivo'),
        (6, 'Receita perigosa'),
        (7, 'Outros'),
    ]
    
    unique_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name="ID Único"
    )
    
    id_receita = models.ForeignKey(
        Receita,
        on_delete=models.CASCADE,
        verbose_name="Receita Denunciada",
        related_name="denuncias"
    )
    
    motivo_denuncia = models.IntegerField(
        choices=MOTIVO_CHOICES,
        verbose_name="Motivo da Denúncia"
    )
    
    detalhamento = models.TextField(
        max_length=280,
        blank=True,
        null=True,
        verbose_name="Detalhamento",
        help_text="Máximo 280 caracteres"
    )
    
    id_denunciante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Denunciante",
        related_name="denuncias_feitas"
    )
    
    data_denuncia = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Denúncia"
    )
    
    class Meta:
        verbose_name = "Denúncia"
        verbose_name_plural = "Denúncias"
        ordering = ['-data_denuncia']
        # Impede que o mesmo usuário denuncie a mesma receita mais de uma vez
        unique_together = ['id_receita', 'id_denunciante']
    
    def __str__(self):
        return f"Denúncia de {self.id_denunciante.username} para receita {self.id_receita.titulo}"
    
    def get_motivo_display_verbose(self):
        """Retorna o motivo da denúncia em formato legível"""
        return dict(self.MOTIVO_CHOICES).get(self.motivo_denuncia, "Não especificado")
