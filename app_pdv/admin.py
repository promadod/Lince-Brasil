from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Loja, PerfilUsuario, Fornecedor, ItemEstoque, Produto, Cliente, 
    Venda, ItemVenda, Caixa, EntradaEstoque, 
    CategoriaTransacao, Transacao, Receita, Despesa, Moto, Motoboy
)

admin.site.site_header = "Magno Distribuidora - Administração"
admin.site.site_title = "Painel Administrativo"
admin.site.index_title = "Gerenciamento do Sistema"

# --- CONFIGURAÇÃO DE USUÁRIO E PERFIL (SAAS) ---
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil do Usuário (Vincular Loja)'

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)

# Remove o admin de usuário padrão e adiciona com a Loja
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# --- HELPER PARA MULTI-LOJAS ---
class SaasAdmin(admin.ModelAdmin):
    """
    Classe auxiliar que adiciona a coluna 'Loja' na visualização
    apenas se o usuário for Superusuário (Dono do SaaS).
    """
    def get_list_display(self, request):
        defaults = list(super().get_list_display(request))
        
        if request.user.is_superuser and 'loja' not in defaults:
            return defaults + ['loja']
        return defaults

    def get_list_filter(self, request):
        defaults = list(super().get_list_filter(request))
        if request.user.is_superuser and 'loja' not in defaults:
            return defaults + ['loja']
        return defaults


# ---  MODELS ORIGINAIS (COM HERANÇA SAAS) ---

@admin.register(Loja)
class LojaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'gerente', 'ativo', 'data_criacao') 
    list_filter = ('ativo',)


@admin.register(Fornecedor)
class FornecedorAdmin(SaasAdmin):
    list_display = ('id', 'nome', 'contato')
    search_fields = ('nome', 'contato')


@admin.register(ItemEstoque)
class ItemEstoqueAdmin(SaasAdmin):
    
    list_display = ('id', 'nome', 'quantidade_estoque', 'status_estoque')
    search_fields = ('nome',)
    list_per_page = 20
    readonly_fields = ('id',) 

    @admin.display(description='Situação')
    def status_estoque(self, obj):
        if obj.quantidade_estoque <= 10:
            return "⚠️ Baixo"
        return "✅ Normal"


@admin.register(Produto)
class ProdutoAdmin(SaasAdmin):
    
    list_display = ('id', 'nome_venda', 'preco_compra', 'preco_venda', 'lucro_unidade', 'fornecedor')
    search_fields = ('nome_venda',)
    list_filter = ('fornecedor',)
    list_editable = ('preco_venda',)
    readonly_fields = ('id',) 
    
    @admin.display(description='Lucro Unit.')
    def lucro_unidade(self, obj):
        return f"R$ {obj.preco_venda - obj.preco_compra:.2f}"


@admin.register(Cliente)
class ClienteAdmin(SaasAdmin):
    list_display = ('id', 'nome', 'whatsapp', 'telefone')
    search_fields = ('nome', 'whatsapp', 'telefone')


# --- VENDAS ---
class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 0
    readonly_fields = ('total_item',)
    
    def total_item(self, obj):
        return f"R$ {obj.quantidade * obj.preco_unitario:.2f}"


@admin.register(Venda)
class VendaAdmin(SaasAdmin):
    list_display = ('id', 'cliente_nome', 'total', 'status', 'forma_pagamento', 'data_venda')
    
    list_filter = ('status', 'forma_pagamento', 'data_venda', 'loja')
    search_fields = ('cliente__nome', 'id')
    inlines = [ItemVendaInline]
    date_hierarchy = 'data_venda'
    
    @admin.display(description='Cliente')
    def cliente_nome(self, obj):
        return obj.cliente.nome if obj.cliente else "Consumidor Final"


@admin.register(Caixa)
class CaixaAdmin(SaasAdmin):
    list_display = ('id', 'data', 'saldo_inicial', 'saldo_final', 'status', 'loja')
    list_filter = ('status', 'data')


@admin.register(EntradaEstoque)
class EntradaEstoqueAdmin(SaasAdmin):
    list_display = ('id', 'item', 'quantidade', 'data_entrada', 'observacao')
    list_filter = ('data_entrada',)
    search_fields = ('item__nome',)


@admin.register(CategoriaTransacao)
class CategoriaTransacaoAdmin(SaasAdmin):
    list_display = ('id', 'nome', 'tipo_formatado')
    list_filter = ('tipo',)

    @admin.display(description='Tipo')
    def tipo_formatado(self, obj):
        return "🟢 Receita" if obj.tipo == 'RECEITA' else "🔴 Despesa"


@admin.register(Receita)
class ReceitaAdmin(SaasAdmin):
    list_display = ('id', 'descricao', 'valor', 'categoria', 'data', 'loja')
    list_filter = ('data', 'categoria')
    search_fields = ('descricao',)
    date_hierarchy = 'data'
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(categoria__tipo='RECEITA')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "categoria":
            kwargs["queryset"] = CategoriaTransacao.objects.filter(tipo='RECEITA')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Despesa)
class DespesaAdmin(SaasAdmin):
    list_display = ('id', 'descricao', 'valor', 'categoria', 'data', 'loja')
    list_filter = ('data', 'categoria')
    search_fields = ('descricao',)
    date_hierarchy = 'data'
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(categoria__tipo='DESPESA')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "categoria":
            kwargs["queryset"] = CategoriaTransacao.objects.filter(tipo='DESPESA')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Transacao)
class TransacaoGeralAdmin(SaasAdmin):
    list_display = ('id', 'descricao', 'valor_formatado', 'categoria', 'data')
    list_filter = ('categoria__tipo', 'data')
    
    @admin.display(description='Valor')
    def valor_formatado(self, obj):
        
        cor = "green" if obj.categoria and obj.categoria.tipo == 'RECEITA' else "red"
        return f"R$ {obj.valor}"


admin.site.register(Moto, SaasAdmin)
admin.site.register(Motoboy, SaasAdmin)