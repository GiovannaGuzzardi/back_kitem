from django.db import models

class Ingrediente(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False, help_text="Nome do ingrediente")

    def __str__(self):
        return self.name
    
    class Meta:
        managed = True
        db_table = 'Ingredient'
        ordering = ['name']
        verbose_name = 'ingrediente'
        verbose_name_plural = 'Ingredientes'    