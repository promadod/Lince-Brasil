from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ------------------ OPÇÕES GERAIS (Status e Origem) ---------------
STATUS_VENDA_CHOICES = [
    ('ABERTO', 'Em Aberto (Balcão)'),
    ('FINALIZADO', 'Finalizado'),
    ('ORCAMENTO', 'Orçamento'),
    ('PENDENTE', 'Aguardando Aprovação'),   
    ('EM_PREPARACAO', 'Em Separação'),      
    ('SAIU_ENTREGA', 'Saiu para Entrega'),  
    ('CANCELADO', 'Cancelado/Recusado'),    
]

ORIGEM_VENDA_CHOICES = [
    ('PDV', 'Balcão/Caixa'),
    ('APP', 'App Cliente'),
]

STATUS_ENTREGA_CHOICES = [
    ('PENDENTE', 'Aguardando Motoboy'),
    ('EM_ROTA', 'Saiu para Entrega'),
    ('ENTREGUE', 'Entregue Finalizado'),
]

FORMA_PGTO_CHOICES = [
    ('DINHEIRO', 'Dinheiro'), 
    ('CREDITO', 'Crédito'), 
    ('DEBITO', 'Débito'), 
    ('PIX', 'Pix')
]

# 1. -----------------------Lojas (SaaS)------------------------
class Loja(models.Model):
    nome = models.CharField(max_length=100)
    gerente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="lojas_gerenciadas")
    taxa_entrega_app = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=5.00, 
        verbose_name="Taxa de Entrega (App)"
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Loja Ativa?")
    data_criacao = models.DateTimeField(auto_now_add=True)
    loja_aberta = models.BooleanField(default=True, verbose_name="Loja Aberta para Delivery")
    
    def __str__(self): return self.nome


class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    
    def __str__(self): return f"{self.user.username} - {self.loja}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    
    if hasattr(instance, 'perfil'):
        instance.perfil.save()

@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def salvar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()


# 2. ------------------------Fornecedores / Item ------------------------
class Fornecedor(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE) 
    nome = models.CharField(max_length=100)
    contato = models.CharField(max_length=50)
    
    def __str__(self): return self.nome

class ItemEstoque(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE) 
    nome = models.CharField(max_length=150, verbose_name="Nome do Item")
    quantidade_estoque = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['nome'] 
        
        unique_together = ('loja', 'nome') 

    def __str__(self): return self.nome

# 3. ---------------------------------------Produtos ----------------------------
class Produto(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE) 
    
    item = models.OneToOneField(ItemEstoque, on_delete=models.CASCADE, related_name="produto_principal", null=True, blank=True)
    item_estoque = models.ForeignKey(ItemEstoque, on_delete=models.CASCADE, verbose_name="Item do Estoque", related_name="produtos_venda")
    
    nome_venda = models.CharField(max_length=150, verbose_name="Nome na Venda (Ex: Pack, Promoção)")
    preco_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço de Custo (Unitário)")
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantidade_baixa = models.IntegerField(default=1, verbose_name="Qtd retirada do estoque (ex: 12 p/ Pack)")
    
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True)
    ativo = models.BooleanField(default=True, verbose_name="Disponível no App?") 
    
    foto = models.ImageField(upload_to='produtos/', null=True, blank=True) 

    def __str__(self): return self.nome_venda

# 4. -----------------------------Clientes-----------------------------------------
class Cliente(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE) 
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    
    def __str__(self): return self.nome

# 5. ---------------------------Vendas e Itens-------------------------------------
class Venda(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE) 
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) 
    
    data_venda = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(max_length=20, choices=STATUS_VENDA_CHOICES, default='ABERTO')
    origem = models.CharField(max_length=10, choices=ORIGEM_VENDA_CHOICES, default='PDV')
    observacao = models.TextField(blank=True, null=True, verbose_name="Obs do Pedido") 
    
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PGTO_CHOICES, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    eh_entrega = models.BooleanField(default=False, verbose_name="É Entrega?")
    endereco_entrega = models.TextField(blank=True, null=True)
    taxa_entrega = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    troco_para = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    conferencia_ok = models.BooleanField(default=False)
    
    status_entrega = models.CharField(
        max_length=20, 
        choices=STATUS_ENTREGA_CHOICES, 
        default='PENDENTE'
    )
    
    entregador = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="entregas_realizadas"
    )

    def __str__(self):
        return f"Venda #{self.id} - {self.get_status_display()}"


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name="itens") 
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1) 
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        if not self.pk and self.venda.status == 'FINALIZADO':
            total_a_baixar = self.quantidade * self.produto.quantidade_baixa
            self.produto.item_estoque.quantidade_estoque -= total_a_baixar
            self.produto.item_estoque.save()
            
        super().save(*args, **kwargs)

# 6. ----------------------------------Caixa---------------------------------
class Caixa(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.BooleanField(default=True) 

# 7. ----------------------------------Estoque -------------------------------
class EntradaEstoque(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE) 
    item = models.ForeignKey(ItemEstoque, on_delete=models.CASCADE) 
    quantidade = models.IntegerField()
    data_entrada = models.DateTimeField(auto_now_add=True)
    observacao = models.CharField(max_length=200, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.pk: 
            self.item.quantidade_estoque += self.quantidade
            self.item.save()
        super().save(*args, **kwargs)
        
    def __str__(self): return f"{self.item.nome} - +{self.quantidade}"

# 8. ------------------------------- Relatorios --------------------------------
class CategoriaTransacao(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE) 
    TIPO_CHOICES = [('RECEITA', 'Receita/Entrada'), ('DESPESA', 'Despesa/Saída')]
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    def __str__(self): return f"{self.nome} ({self.get_tipo_display()})"

class Transacao(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaTransacao, on_delete=models.SET_NULL, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(auto_now_add=True)
    descricao = models.CharField(max_length=200, blank=True, null=True) 
    
    def __str__(self): return f"R$ {self.valor} - {self.categoria}"

class Receita(Transacao):
    class Meta:
        proxy = True
        verbose_name = "Receita / Entrada"
        verbose_name_plural = "Receitas"

class Despesa(Transacao):
    class Meta:
        proxy = True
        verbose_name = "Despesa / Saída"
        verbose_name_plural = "Despesas"

#9.---------------------------- Motoboy / Entregas-----------------------------

class Motoboy(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='motoboy_perfil')
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    telefone = models.CharField(max_length=20, verbose_name="WhatsApp/Telefone")
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.nome

class Moto(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE) 
    modelo = models.CharField(max_length=50, help_text="Ex: Honda CG 160")
    placa = models.CharField(max_length=10) 
    cor = models.CharField(max_length=20)
    ativa = models.BooleanField(default=True)

    def __str__(self): return f"{self.modelo} - {self.placa}"