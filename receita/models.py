from django.db import models
# pq importar user? pq o django ja tem um user padrao, e se eu quiser usar ele, eu preciso importar
# e fazer referencia a ele, caso contrario, eu teria que criar um user do zero, o que seria mais trabalhoso
from django.contrib.auth.models import User as Usuario
from ingrediente.models import Ingrediente

class Receita(models.Model):
    # Categorias pré-determinadas inspiradas em sites de receitas
    CATEGORIA_CHOICES = [
        ('massas', 'Massas'),
        ('carnes', 'Carnes'),
        ('aves', 'Aves'),
        ('peixes_frutos_mar', 'Peixes e Frutos do Mar'),
        ('vegetarianos', 'Pratos Vegetarianos'),
        ('veganos', 'Pratos Veganos'),
        ('sopas_caldos', 'Sopas e Caldos'),
        ('saladas', 'Saladas'),
        ('risotos', 'Risotos'),
        ('pizzas', 'Pizzas'),
        ('lanches_sanduiches', 'Lanches e Sanduíches'),
        ('aperitivos', 'Aperitivos'),
        ('bolos', 'Bolos'),
        ('tortas_doces', 'Tortas Doces'),
        ('tortas_salgadas', 'Tortas Salgadas'),
        ('sobremesas', 'Sobremesas'),
        ('doces_brigadeiros', 'Doces e Brigadeiros'),
        ('paes', 'Pães'),
        ('biscoitos', 'Biscoitos'),
        ('bebidas', 'Bebidas'),
        ('sucos_vitaminas', 'Sucos e Vitaminas'),
        ('molhos_temperos', 'Molhos e Temperos'),
        ('acompanhamentos', 'Acompanhamentos'),
        ('arroz_feijao', 'Arroz e Feijão'),
        ('comida_mineira', 'Comida Mineira'),
        ('comida_italiana', 'Comida Italiana'),
        ('comida_japonesa', 'Comida Japonesa'),
        ('comida_mexicana', 'Comida Mexicana'),
        ('comida_chinesa', 'Comida Chinesa'),
        ('comida_arabe', 'Comida Árabe'),
        ('fit_light', 'Fit e Light'),
        ('sem_gluten', 'Sem Glúten'),
        ('sem_lactose', 'Sem Lactose'),
        ('diabeticos', 'Para Diabéticos'),
        ('infantil', 'Comida Infantil'),
        ('festa_aniversario', 'Festa e Aniversário'),
        ('natal_ano_novo', 'Natal e Ano Novo'),
        ('pascoa', 'Páscoa'),
        ('festa_junina', 'Festa Junina'),
        ('outros', 'Outros'),
    ]
    
    id = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='receitas')
    titulo = models.CharField(max_length=50, null=False)
    descricao = models.CharField(max_length=1500, null=False)
    tempo_preparo = models.TimeField(null=False)
    dificuldade = models.CharField(max_length=25, null=False)
    tipo = models.CharField(max_length=25, null=True)
    restricao_alimentar = models.CharField(max_length=25, null=True)
    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIA_CHOICES,
        default='outros',
        null=True,
        blank=True,
        verbose_name='Categoria',
        help_text='Categoria da receita'
    )
    imagem = models.URLField(max_length=600, null=True)
    quantidade_visualizacao = models.IntegerField(default=0, null=False)

    def __str__(self):
        return self.titulo
    
    def get_categoria_display_verbose(self):
        """Retorna a categoria em formato legível"""
        return dict(self.CATEGORIA_CHOICES).get(self.categoria, "Não especificada")

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
