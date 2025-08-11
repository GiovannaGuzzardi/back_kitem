from django.db import models

class Ingrediente(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, null=False, help_text="Nome do ingrediente")

    # self é a referência para a própria instância da classe
    # exemplo: tenho uma instancia da classe ingrediente chamada "ingrediente1" com nome "sal"
    # quando eu chamo o método __str__() em ingrediente1, ele retorna o nome "sal"
    def __str__(self):
        return self.nome
    
    # essa classe Meta é uma classe interna que define metadados para o modelo
    # metadados são informações adicionais sobre o modelo, como o nome da tabela no banco de dados
    class Meta:
        # managed = true significa que o Django irá gerenciar a tabela no banco de dados
        managed = True
        # db_table define o nome da tabela no banco de dados
        db_table = 'tab_ingrediente'
        # ordering define a ordem padrão de exibição dos objetos do modelo
        ordering = ['id']
        # verbose_name e verbose_name_plural definem os nomes exibidos no admin do Django
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'    