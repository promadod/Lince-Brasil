from django import forms
from .models import Produto, Cliente, Fornecedor, EntradaEstoque, Loja, ItemEstoque, CategoriaTransacao, Transacao, Motoboy, Moto
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



class ItemEstoqueForm(forms.ModelForm):
    class Meta:
        model = ItemEstoque
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Coca Cola 2L'}),
        }

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        
        fields = ['item_estoque', 'nome_venda', 'quantidade_baixa', 'preco_compra', 'preco_venda', 'fornecedor']
        
        labels = {
            'item_estoque': 'Item do Estoque (Pai)', 
            'nome_venda': 'Nome de Venda (Ex: Pack c/ 12)',
            'quantidade_baixa': 'Qtd Itens neste Produto (Ex: 12)',
            'preco_compra': 'Preço de Custo (Unitário)',
            'preco_venda': 'Preço de Venda (Deste pacote)',
            'fornecedor': 'Fornecedor'
        }
        
        widgets = {
            
            'item_estoque': forms.Select(attrs={'class': 'form-control'}),
            'nome_venda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Coca Cola Fardo'}),
            'quantidade_baixa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1 para avulso, 12 para fardo...'}),
            'preco_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_venda': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fornecedor': forms.Select(attrs={'class': 'form-control'}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'telefone', 'whatsapp', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'contato']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'contato': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LojaForm(forms.ModelForm):
    class Meta:
        model = Loja
        fields = ['nome', 'gerente']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'gerente': forms.Select(attrs={'class': 'form-control'}),
        }

class EntradaEstoqueForm(forms.ModelForm):
    class Meta:
        model = EntradaEstoque
        fields = ['item', 'quantidade', 'observacao']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}), 
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional (ex: NF de compra)'}),
        }


class CategoriaTransacaoForm(forms.ModelForm):
    class Meta:
        model = CategoriaTransacao
        fields = ['nome', 'tipo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Conta de Luz'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
        }

class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['categoria', 'valor', 'descricao']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Detalhes (Opcional)'}),
        }

class ImportacaoForm(forms.Form):
    arquivo_excel = forms.FileField(label="Selecione o arquivo Excel (.xlsx)", widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx'}))

class CadastroVendedorForm(UserCreationForm):
    
    first_name = forms.CharField(label="Nome", max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Ana'}))
    last_name = forms.CharField(label="Sobrenome", max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Souza'}))
    username = forms.CharField(label="Usuário (Login)", max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: anasouza'}))
    email = forms.EmailField(label="E-mail (Opcional)", required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']



class MotoboyForm(forms.ModelForm):
    class Meta:
        model = Motoboy
        fields = ['nome', 'cpf', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) 9XXXX-XXXX'}),
        }

class MotoForm(forms.ModelForm):
    class Meta:
        model = Moto
        fields = ['modelo', 'placa', 'cor']
        widgets = {
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Fan 160'}),
            'placa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ABC-1234'}),
            'cor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Vermelha'}),
        }