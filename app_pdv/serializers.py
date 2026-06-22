from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Venda, ItemVenda, Produto, Cliente

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'is_superuser']


class ProdutoCatalogoSerializer(serializers.ModelSerializer):
    estoque_atual = serializers.IntegerField(source='item_estoque.quantidade_estoque', read_only=True)
    preco_venda = serializers.FloatField()
    class Meta:
        model = Produto
        fields = ['id', 'nome_venda', 'preco_venda','estoque_atual','imagem']
        

class ItemVendaSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome_venda', read_only=True)

    class Meta:
        model = ItemVenda
        fields = ['id', 'produto', 'produto_nome', 'quantidade', 'preco_unitario', 'custo_unitario']

class VendaSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True, allow_null=True)
    
    
    itens = ItemVendaSerializer(many=True, read_only=True)

    class Meta:
        model = Venda
        fields = [
            'id', 
            'cliente_nome', 
            'total', 
            'data_venda', 
            'status', 
            'origem', 
            'observacao', 
            'eh_entrega', 
            'endereco_entrega', 
            'status_entrega', 
            'taxa_entrega',
            'itens'
        ]