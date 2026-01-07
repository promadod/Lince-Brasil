'''SUMARIO DE FUNÇÕES 
45   | HELPER FUNCTION (SAAS)
70   | PRODUTOS
142  | CLIENTES
178  | VENDAS
365  | DASHBOARD
436  | FORNECEDORES
469  | LOJAS
502  | CAIXA
583  | ESTOQUE
607  | GESTÃO DE CATEGORIAS
637  | LANÇAR RECEITAS / DESPESAS NO CAIXA
660  | CENTRAL  DE RELATORIOS
853  | IMPORTAÇÃO
995  | VENDEDOR
1030 | ENTREGAS(MOTOBOY)
1110 | APP DO MOTOBOY (FLUTTER)
1261 | AREA DE APIS (DEMAIS ENDPOINTS)
1312 | FUNÇÃO AJUDANTE
1457 | APP DO CLIENTE E TORRE DE CONTROLE
'''
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDate
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import make_aware
from datetime import datetime, date, timedelta
import json
import pandas as pd

# Imports de Models e Forms 
from .models import (
    Venda, ItemVenda, Produto, Cliente, Fornecedor, Loja, 
    CategoriaTransacao, Transacao, Caixa, Motoboy, Moto, 
    EntradaEstoque, ItemEstoque, PerfilUsuario
)
from .forms import (
    ProdutoForm, ClienteForm, FornecedorForm, LojaForm, 
    CategoriaTransacaoForm, TransacaoForm, ImportacaoForm, 
    CadastroVendedorForm, MotoboyForm, MotoForm, 
    EntradaEstoqueForm, ItemEstoqueForm
)
from django.contrib.auth.models import User, Group

# Imports DRF (API)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer, ProdutoCatalogoSerializer

# ------------------------- HELPER FUNCTION (SAAS) -------------------------------------
def get_loja_usuario(user):
    """
    Retorna a loja vinculada ao usuário.
    Se não tiver loja, retorna None ou lança erro.
    """
    try:
        if user.is_superuser:
            
            if hasattr(user, 'perfil') and user.perfil.loja:
                return user.perfil.loja
            return Loja.objects.first()
        
        return user.perfil.loja
    except AttributeError:
        return None

def check_loja(request):
    """Verifica se o usuário tem loja, senão redireciona ou avisa"""
    loja = get_loja_usuario(request.user)
    if not loja:
        messages.error(request, "Seu usuário não está vinculado a nenhuma Loja. Contate o suporte.")
        return None
    return loja

# --------------------------- PRODUTOS (ESTOQUE) ------------------------------------


@login_required
def lista_produtos(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')
    
    produtos = Produto.objects.filter(loja=loja).order_by('item_estoque__nome') 
    return render(request, 'app_pdv/lista_produtos.html', {'produtos': produtos})

@login_required
def gerenciar_produto(request, id=None):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')

    produto = get_object_or_404(Produto, pk=id, loja=loja) if id else None
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.loja = loja # Vincula à loja
            obj.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm(instance=produto)
    
    return render(request, 'app_pdv/form_generico.html', {'form': form, 'titulo': 'Cadastro de Produto'})

@login_required
def deletar_produto(request, id):
    loja = check_loja(request)
    produto = get_object_or_404(Produto, pk=id, loja=loja)
    produto.delete()
    return redirect('lista_produtos')

@login_required
def lista_itens(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')
    
    itens = ItemEstoque.objects.filter(loja=loja).order_by('nome')
    return render(request, 'app_pdv/lista_itens.html', {'itens': itens})

@login_required
def gerenciar_item(request, id=None):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')

    item = get_object_or_404(ItemEstoque, pk=id, loja=loja) if id else None
    
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST, instance=item)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.loja = loja
            obj.save()
            return redirect('lista_itens')
    else:
        form = ItemEstoqueForm(instance=item)
    
    return render(request, 'app_pdv/form_generico.html', {'form': form, 'titulo': 'Cadastrar Item no Estoque'})

@login_required
def deletar_item(request, id):
    loja = check_loja(request)
    item = get_object_or_404(ItemEstoque, pk=id, loja=loja)
    item.delete()
    return redirect('lista_itens')


# ---------------------------------- CLIENTES ----------------------------------------------
@login_required
def lista_clientes(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')

    clientes = Cliente.objects.filter(loja=loja).order_by('nome')
    return render(request, 'app_pdv/lista_clientes.html', {'clientes': clientes})

@login_required
def deletar_cliente(request, id):
    loja = check_loja(request)
    cliente = get_object_or_404(Cliente, pk=id, loja=loja)
    cliente.delete()
    return redirect('lista_clientes')

@login_required
def gerenciar_cliente(request, id=None):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')

    cliente = get_object_or_404(Cliente, pk=id, loja=loja) if id else None
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.loja = loja
            obj.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'app_pdv/form_generico.html', {'form': form, 'titulo': 'Cadastro de Cliente'})


# ----------------------------- VENDAS ------------------------------------

@login_required
def lista_vendas(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')

    vendas = Venda.objects.filter(loja=loja).order_by('-data_venda')
    return render(request, 'app_pdv/lista_vendas.html', {'vendas': vendas})

@login_required
def detalhes_venda(request, id):
    loja = check_loja(request)
    venda = get_object_or_404(Venda, pk=id, loja=loja)
    itens = ItemVenda.objects.filter(venda=venda)
    return render(request, 'app_pdv/detalhes_venda.html', {'venda': venda, 'itens': itens})

@login_required
def nova_venda(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')

    produtos = Produto.objects.filter(loja=loja, item_estoque__quantidade_estoque__gt=0) 
    clientes = Cliente.objects.filter(loja=loja)
    return render(request, 'app_pdv/vendas.html', {'produtos': produtos, 'clientes': clientes})

@login_required
def excluir_venda(request, id):
    loja = check_loja(request)
    venda = get_object_or_404(Venda, pk=id, loja=loja)
    
    if venda.status in ['ABERTO', 'ORCAMENTO']:
        venda.delete()
    
    return redirect('lista_vendas')

@transaction.atomic 
@login_required
def salvar_venda(request):
    loja = check_loja(request)
    if not loja: 
        return JsonResponse({'status': 'erro', 'mensagem': 'Usuário sem loja vinculada'}, status=403)

    if request.method == 'POST':
        data = json.loads(request.body)
        
        
        eh_entrega = data.get('eh_entrega', False)
        endereco_entrega = "" 
        
        if eh_entrega:
            cliente_id = data.get('cliente_id')
            if cliente_id:
                try:
                    cli = Cliente.objects.get(id=cliente_id, loja=loja)
                    endereco_entrega = cli.endereco if cli.endereco else "Endereço não cadastrado no cliente"
                except Cliente.DoesNotExist:
                    endereco_entrega = "Cliente não encontrado"
            else:
                endereco_entrega = "Cliente Avulso"

        status_entrega_inicial = 'PENDENTE' if eh_entrega else ''
        
        venda_id = data.get('venda_id') 
        valor_troco = data.get('troco_para')
        if not valor_troco or valor_troco == '':
            valor_troco = 0

        if venda_id:
            
            try:
                venda = Venda.objects.get(id=venda_id, loja=loja)
                venda.cliente_id = data.get('cliente_id') if data.get('cliente_id') else None
                venda.status = data.get('status', 'FINALIZADO')
                venda.forma_pagamento = data.get('forma_pagamento')
                venda.taxa_entrega = data.get('taxa_entrega', 0)
                venda.total = data.get('total_final')
                venda.troco_para = valor_troco
                venda.eh_entrega = eh_entrega
                venda.endereco_entrega = endereco_entrega
                if eh_entrega:
                    venda.status_entrega = 'PENDENTE'
                
                venda.save()
                
                ItemVenda.objects.filter(venda=venda).delete()
                nova_venda = venda 
            except Venda.DoesNotExist:
                 return JsonResponse({'status': 'erro', 'mensagem': 'Venda não encontrada'}, status=404)
        else:
            
            nova_venda = Venda.objects.create(
                loja=loja, 
                cliente_id=data.get('cliente_id') if data.get('cliente_id') else None,
                vendedor=request.user,
                status=data.get('status', 'FINALIZADO'),
                forma_pagamento=data.get('forma_pagamento'),
                taxa_entrega=data.get('taxa_entrega', 0),
                total=data.get('total_final'),
                eh_entrega=eh_entrega,
                endereco_entrega=endereco_entrega,
                status_entrega=status_entrega_inicial,
                troco_para=valor_troco
            )

        
        for item in data['itens']:
            try:
                produto = Produto.objects.get(id=item['id'], loja=loja)
                ItemVenda.objects.create(
                    venda=nova_venda,
                    produto=produto,
                    quantidade=item['quantidade'],
                    preco_unitario=item['preco']
                )
            except Produto.DoesNotExist:
                pass 

        return JsonResponse({'status': 'sucesso', 'venda_id': nova_venda.id})
        
    return JsonResponse({'status': 'erro', 'mensagem': 'Método inválido'}, status=400)



@login_required
@transaction.atomic
def cancelar_venda_pdv(request, id):
    loja = check_loja(request)
    venda = get_object_or_404(Venda, pk=id, loja=loja)
    
    # Proteção: Se já estiver cancelada, não faz nada para não duplicar estoque
    if venda.status == 'CANCELADO':
        messages.warning(request, 'Esta venda já foi cancelada anteriormente.')
        return redirect('detalhes_venda', id=id)

    # 1. Devolver itens ao estoque (Estorno)
    itens = ItemVenda.objects.filter(venda=venda)
    for item_venda in itens:
        produto = item_venda.produto
        # Calcula quanto saiu do estoque na venda (Qtd Venda * Fator do Produto)
        qtd_a_devolver = item_venda.quantidade * produto.quantidade_baixa
        
        # Devolve ao estoque principal
        item_estoque = produto.item_estoque
        item_estoque.quantidade_estoque += qtd_a_devolver
        item_estoque.save()

    # 2. Atualizar status da venda
    venda.status = 'CANCELADO'
    venda.save()
    
    messages.success(request, f'Venda #{venda.id} cancelada e estoque estornado com sucesso!')
    return redirect('detalhes_venda', id=id)

@login_required
def retomar_venda(request, id):
    loja = check_loja(request)
    venda = get_object_or_404(Venda, pk=id, loja=loja)
    
    if venda.status == 'FINALIZADO':
        return redirect('lista_vendas')

    itens_venda = ItemVenda.objects.filter(venda=venda)
    lista_itens = []
    
    for item in itens_venda:
        lista_itens.append({
            'id': item.produto.id,
            'nome': item.produto.nome_venda, 
            'preco': float(item.preco_unitario),
            'quantidade': item.quantidade
        })
    
    itens_json = json.dumps(lista_itens, cls=DjangoJSONEncoder)
    
    produtos = Produto.objects.filter(loja=loja, item_estoque__quantidade_estoque__gt=0)
    clientes = Cliente.objects.filter(loja=loja)

    context = {
        'venda_aberta': venda, 
        'itens_json': itens_json, 
        'produtos': produtos,
        'clientes': clientes,
    }
    return render(request, 'app_pdv/vendas.html', context)


# ------------------------- DASHBOARD ------------------------------

@login_required
def dashboard(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')
   
    hoje = datetime.now()
    ano = hoje.year
    mes = hoje.month

    vendas_mes_qs = Venda.objects.filter(
        loja=loja,
        data_venda__year=ano, 
        data_venda__month=mes,
        status='FINALIZADO'
    )

    faturamento_total = vendas_mes_qs.aggregate(Sum('total'))['total__sum'] or 0
    
    melhor_cliente = vendas_mes_qs.values('cliente__nome').annotate(
        total_gasto=Sum('total')
    ).order_by('-total_gasto').first()

    produto_campeao_qs = ItemVenda.objects.filter(
        venda__loja=loja,
        venda__data_venda__year=ano,
        venda__data_venda__month=mes,
        venda__status='FINALIZADO'
    ).values('produto__nome_venda').annotate(
        lucro_total=Sum((F('preco_unitario') - F('produto__preco_compra')) * F('quantidade'))
    ).order_by('-lucro_total').first()

    estoque_baixo = ItemEstoque.objects.filter(
        loja=loja,
        quantidade_estoque__lte=10
    ).order_by('quantidade_estoque')[:2]

    data_inicio_grafico = hoje - timedelta(days=15)
    
    vendas_diarias = Venda.objects.filter(
        loja=loja,
        data_venda__date__gte=data_inicio_grafico,
        status='FINALIZADO'
    ).annotate(
        data_formatada=TruncDate('data_venda')
    ).values('data_formatada').annotate(
        total=Sum('total')
    ).order_by('data_formatada')
    
    grafico_datas = []
    grafico_valores = []
    
    for v in vendas_diarias:
        grafico_datas.append(v['data_formatada'].strftime('%d/%m'))
        grafico_valores.append(float(v['total']))

    ultimas_vendas = Venda.objects.filter(loja=loja).select_related('cliente').order_by('-data_venda')[:6]

    context = {
        'vendas_mes': faturamento_total,
        'melhor_cliente': melhor_cliente,
        'produto_campeao': produto_campeao_qs,
        'estoque_baixo': estoque_baixo,
        'ultimas_vendas': ultimas_vendas,
        'grafico_labels': json.dumps(grafico_datas),  
        'grafico_data': json.dumps(grafico_valores),
    }
    return render(request, 'app_pdv/dashboard.html', context)


# ---------------------- FORNECEDORES -----------------------------------

@login_required
def deletar_fornecedor(request, id):
    loja = check_loja(request)
    get_object_or_404(Fornecedor, pk=id, loja=loja).delete()
    return redirect('lista_fornecedores')

@login_required
def lista_fornecedores(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')
    fornecedores = Fornecedor.objects.filter(loja=loja)
    return render(request, 'app_pdv/lista_fornecedores.html', {'fornecedores': fornecedores})

@login_required
def gerenciar_fornecedor(request, id=None):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')

    fornecedor = get_object_or_404(Fornecedor, pk=id, loja=loja) if id else None
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.loja = loja
            obj.save()
            return redirect('lista_fornecedores')
    else:
        form = FornecedorForm(instance=fornecedor)
    return render(request, 'app_pdv/form_generico.html', {'form': form, 'titulo': 'Fornecedor'})


# -------------------------- LOJAS (Apenas SuperAdmin ou Dono vê) --------------------------------------
@login_required
def lista_lojas(request):
    
    if request.user.is_superuser:
        lojas = Loja.objects.all()
    else:
        lojas = Loja.objects.filter(id=request.user.perfil.loja.id)
        
    return render(request, 'app_pdv/lista_lojas.html', {'lojas': lojas})

@login_required
def gerenciar_loja(request, id=None):
    
    loja_usuario = check_loja(request)
    
    if not request.user.is_superuser:
        
        if str(id) != str(loja_usuario.id):
             messages.error(request, "Você não tem permissão para editar outras lojas.")
             return redirect('lista_lojas')

    loja = get_object_or_404(Loja, pk=id) if id else None
    if request.method == 'POST':
        form = LojaForm(request.POST, instance=loja)
        if form.is_valid():
            form.save()
            return redirect('lista_lojas')
    else:
        form = LojaForm(instance=loja)
    return render(request, 'app_pdv/form_generico.html', {'form': form, 'titulo': 'Loja'})


# ---------------------------- CAIXA --------------------------------

@login_required
def fluxo_caixa(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')
    
    hoje = date.today()
    caixa_hoje = Caixa.objects.filter(loja=loja, data=hoje).first()
    
    if request.method == 'POST' and not caixa_hoje:
        saldo_inicial = request.POST.get('saldo_inicial')
        if loja:
            caixa_hoje = Caixa.objects.create(loja=loja, saldo_inicial=saldo_inicial)
            return redirect('fluxo_caixa')

    vendas_hoje = Venda.objects.filter(loja=loja, data_venda__date=hoje, status='FINALIZADO')
    total_vendas = vendas_hoje.aggregate(Sum('total'))['total__sum'] or 0
    total_dinheiro = vendas_hoje.filter(forma_pagamento='DINHEIRO').aggregate(Sum('total'))['total__sum'] or 0
    total_pix = vendas_hoje.filter(forma_pagamento='PIX').aggregate(Sum('total'))['total__sum'] or 0
    total_credito = vendas_hoje.filter(forma_pagamento='CREDITO').aggregate(Sum('total'))['total__sum'] or 0
    total_debito = vendas_hoje.filter(forma_pagamento='DEBITO').aggregate(Sum('total'))['total__sum'] or 0

    saldo_inicial = caixa_hoje.saldo_inicial if caixa_hoje else 0
    saldo_atual_caixa = saldo_inicial + total_dinheiro

    context = {
        'hoje': hoje,
        'caixa_aberto': caixa_hoje is not None,
        'saldo_inicial': saldo_inicial,
        'saldo_atual_caixa': saldo_atual_caixa, 
        'total_vendas': total_vendas,
        'resumo': {
            'dinheiro': total_dinheiro,
            'pix': total_pix,
            'credito': total_credito,
            'debito': total_debito
        }
    }
    return render(request, 'app_pdv/caixa.html', context)

@login_required
def fechar_caixa(request):
    loja = check_loja(request)
    hoje = datetime.now()
    caixa = Caixa.objects.filter(loja=loja, data=hoje, status=True).first() 
    
    if not caixa:
        return redirect('fluxo_caixa') 

    if request.method == 'POST':
        vendas = Venda.objects.filter(loja=loja, data_venda__date=hoje, status='FINALIZADO')
        
        total_vendas = vendas.aggregate(Sum('total'))['total__sum'] or 0
        dinheiro_vendas = vendas.filter(forma_pagamento='DINHEIRO').aggregate(Sum('total'))['total__sum'] or 0
        
        transacoes = Transacao.objects.filter(loja=loja, data=hoje)
        entradas = transacoes.filter(categoria__tipo='RECEITA').aggregate(Sum('valor'))['valor__sum'] or 0
        saidas = transacoes.filter(categoria__tipo='DESPESA').aggregate(Sum('valor'))['valor__sum'] or 0

        saldo_final_calculado = caixa.saldo_inicial + dinheiro_vendas + entradas - saidas

        caixa.saldo_final = saldo_final_calculado
        caixa.status = False 
        caixa.save()

        context = {
            'caixa': caixa,
            'operador': request.user,
            'data_fechamento': datetime.now(),
            'total_vendas': total_vendas,
            'dinheiro_vendas': dinheiro_vendas, 
            'entradas': entradas,
            'saidas': saidas,
            'resumo_pgto': vendas.values('forma_pagamento').annotate(total=Sum('total'))
        }
        return render(request, 'app_pdv/recibo_fechamento.html', context)
    
    return redirect('fluxo_caixa')


# -------------------------- Estoque --------------------------------------

@login_required
def lista_estoque(request):
    loja = check_loja(request)
    itens = ItemEstoque.objects.filter(loja=loja).order_by('nome')
    return render(request, 'app_pdv/lista_estoque.html', {'itens': itens})

@login_required
def adicionar_estoque(request):
    loja = check_loja(request)
    if request.method == 'POST':
        form = EntradaEstoqueForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.loja = loja
            obj.save() 
            return redirect('lista_estoque')
    else:
        form = EntradaEstoqueForm()
    
    return render(request, 'app_pdv/form_generico.html', {'form': form, 'titulo': 'Abastecer Estoque (Entrada)'})


# ---------------------- GESTÃO DE CATEGORIAS  --------------------------


@login_required
def lista_categorias(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')

    categorias = CategoriaTransacao.objects.filter(loja=loja).order_by('tipo', 'nome')
    
    if request.method == 'POST':
        form = CategoriaTransacaoForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.loja = loja
            obj.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaTransacaoForm()
    return render(request, 'app_pdv/lista_categorias.html', {'categorias': categorias, 'form': form})

@login_required
def deletar_categoria(request, id):
    loja = check_loja(request)
    cat = get_object_or_404(CategoriaTransacao, pk=id, loja=loja)
    cat.delete()
    return redirect('lista_categorias')



# ------------------------- LANÇAR DESPESA/RECEITA NO CAIXA ---------------------------



@login_required
def adicionar_transacao(request):
    loja = check_loja(request)
    if request.method == 'POST':
        form = TransacaoForm(request.POST)
        if form.is_valid():
            transacao = form.save(commit=False)
            transacao.loja = loja 
            transacao.save()
            return redirect('fluxo_caixa')
    else:
        form = TransacaoForm()
        
        form.fields['categoria'].queryset = CategoriaTransacao.objects.filter(loja=loja)
        
    return render(request, 'app_pdv/form_generico.html', {'form': form, 'titulo': 'Lançar Receita ou Despesa'})



# ------------------------------------ CENTRAL DE RELATÓRIOS ---------------------------
@login_required
def relatorios(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')

    data_inicio = request.GET.get('data_inicio', datetime.now().strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', datetime.now().strftime('%Y-%m-%d'))
    tipo_relatorio = request.GET.get('tipo_relatorio', 'financeiro') 

    context = {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_relatorio': tipo_relatorio
    }

    # --- 1. RELATÓRIO FINANCEIRO ---
    if tipo_relatorio == 'financeiro':
        total_vendas = Venda.objects.filter(
            loja=loja,
            data_venda__date__range=[data_inicio, data_fim], 
            status='FINALIZADO'
        ).aggregate(Sum('total'))['total__sum'] or 0

        transacoes = Transacao.objects.filter(loja=loja, data__range=[data_inicio, data_fim])
        receitas_extras = transacoes.filter(categoria__tipo='RECEITA').aggregate(Sum('valor'))['valor__sum'] or 0
        despesas = transacoes.filter(categoria__tipo='DESPESA').aggregate(Sum('valor'))['valor__sum'] or 0

        context['financeiro'] = {
            'vendas': total_vendas,
            'receitas_extras': receitas_extras,
            'total_receitas': total_vendas + receitas_extras,
            'despesas': despesas,
            'saldo_periodo': (total_vendas + receitas_extras) - despesas,
            'lista_transacoes': transacoes
        }

    # --- 2. RELATÓRIO DE ORIGEM (APP x PDV) ---
    elif tipo_relatorio == 'origem':
        vendas_periodo = Venda.objects.filter(loja=loja, data_venda__date__range=[data_inicio, data_fim], status='FINALIZADO')
        
        total_app = vendas_periodo.filter(origem='APP').aggregate(Sum('total'))['total__sum'] or 0
        total_pdv = vendas_periodo.filter(origem='PDV').aggregate(Sum('total'))['total__sum'] or 0

        context['dados_origem'] = {
            'total_app': total_app,
            'qtd_app': vendas_periodo.filter(origem='APP').count(),
            'total_pdv': total_pdv,
            'qtd_pdv': vendas_periodo.filter(origem='PDV').count(),
            'total_geral': total_app + total_pdv,
        }

    # --- 3. RELATÓRIO: FORMA DE PAGAMENTO ---
    elif tipo_relatorio == 'pagamento':
        vendas_periodo = Venda.objects.filter(loja=loja, data_venda__date__range=[data_inicio, data_fim], status='FINALIZADO')

        def get_dados(metodo):
            qs = vendas_periodo.filter(forma_pagamento=metodo)
            return {
                'total': qs.aggregate(Sum('total'))['total__sum'] or 0,
                'qtd': qs.count()
            }

        dinheiro = get_dados('DINHEIRO')
        pix = get_dados('PIX')
        credito = get_dados('CREDITO')
        debito = get_dados('DEBITO')
        total_geral = dinheiro['total'] + pix['total'] + credito['total'] + debito['total']

        context['dados_pagamento'] = {
            'dinheiro': dinheiro,
            'pix': pix,
            'credito': credito,
            'debito': debito,
            'total_geral': total_geral,
        }

    # --- 4. RELATÓRIO DE PRODUTOS ---
    elif tipo_relatorio == 'produtos':
        itens_vendidos = ItemVenda.objects.filter(
            venda__loja=loja,
            venda__data_venda__date__range=[data_inicio, data_fim], venda__status='FINALIZADO'
        ).values('produto__nome_venda', 'produto__preco_compra').annotate(
            qtd_total=Sum('quantidade'), valor_total_vendido=Sum(F('quantidade') * F('preco_unitario'))
        ).order_by('-valor_total_vendido')

        lista_produtos = []
        for item in itens_vendidos:
            custo = (item['produto__preco_compra'] or 0) * item['qtd_total']
            lista_produtos.append({
                'nome': item['produto__nome_venda'], 'qtd': item['qtd_total'],
                'custo_total': custo, 'venda_total': item['valor_total_vendido'],
                'lucro': item['valor_total_vendido'] - custo
            })
        context['produtos'] = lista_produtos

    # --- 5. RELATÓRIO DE CLIENTES ---
    elif tipo_relatorio == 'clientes':
        ranking = Venda.objects.filter(
            loja=loja,
            data_venda__date__range=[data_inicio, data_fim], status='FINALIZADO', cliente__isnull=False 
        ).values('cliente__nome').annotate(
            total_gasto=Sum('total'), qtd_compras=Count('id')
        ).order_by('-total_gasto')
        context['clientes'] = ranking

    # --- 6. RELATÓRIO DE FECHAMENTOS ---
    elif tipo_relatorio == 'fechamentos':
        context['fechamentos'] = Caixa.objects.filter(loja=loja, status=False).order_by('-data')

    # --- 7. RELATÓRIO DE ENTREGADORES ---
    elif tipo_relatorio == 'entregadores':
        vendas_base = Venda.objects.filter(loja=loja, status_entrega='ENTREGUE', data_venda__date__range=[data_inicio, data_fim])
        ids_motoboys = vendas_base.values_list('entregador', flat=True).distinct()
        
        lista_agrupada = []
        total_geral = 0
        for user_id in ids_motoboys:
            if user_id:
                motoboy = User.objects.get(id=user_id)
                vendas_moto = vendas_base.filter(entregador=motoboy)
                total = vendas_moto.aggregate(Sum('taxa_entrega'))['taxa_entrega__sum'] or 0
                lista_agrupada.append({'motoboy': motoboy, 'vendas': vendas_moto, 'total_valor': total, 'quantidade': vendas_moto.count()})
                total_geral += total
        
        context['lista_agrupada'] = lista_agrupada
        context['total_geral_entregas'] = total_geral

    return render(request, 'app_pdv/relatorios.html', context)

@login_required
def ver_recibo_fechamento(request, id):
    loja = check_loja(request)
    caixa = get_object_or_404(Caixa, pk=id, loja=loja)
    
    vendas = Venda.objects.filter(loja=loja, data_venda__date=caixa.data, status='FINALIZADO')
    total_vendas = vendas.aggregate(Sum('total'))['total__sum'] or 0
    dinheiro_vendas = vendas.filter(forma_pagamento='DINHEIRO').aggregate(Sum('total'))['total__sum'] or 0
    
    transacoes = Transacao.objects.filter(loja=loja, data=caixa.data)
    entradas = transacoes.filter(categoria__tipo='RECEITA').aggregate(Sum('valor'))['valor__sum'] or 0
    saidas = transacoes.filter(categoria__tipo='DESPESA').aggregate(Sum('valor'))['valor__sum'] or 0
    
    context = {
        'caixa': caixa,
        'operador': request.user, 
        'data_fechamento': datetime.combine(caixa.data, datetime.min.time()), 
        'total_vendas': total_vendas,
        'dinheiro_vendas': dinheiro_vendas,
        'entradas': entradas,
        'saidas': saidas,
        'resumo_pgto': vendas.values('forma_pagamento').annotate(total=Sum('total'))
    }
    return render(request, 'app_pdv/recibo_fechamento.html', context)


@login_required 
def relatorio_entregadores(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')

    periodo = request.GET.get('periodo', 'hoje')
    motoboy_id = request.GET.get('motoboy') 
    
    hoje = date.today()
    filtro_data = {}
    
    if periodo == 'hoje':
        filtro_data['data_venda__date'] = hoje
    elif periodo == 'mes':
        filtro_data['data_venda__month'] = hoje.month
        filtro_data['data_venda__year'] = hoje.year

    vendas = Venda.objects.filter(loja=loja, status_entrega='ENTREGUE', **filtro_data)

    if motoboy_id:
        vendas = vendas.filter(entregador_id=motoboy_id)

    total_geral = vendas.aggregate(Sum('total'))['total__sum'] or 0
    quantidade = vendas.count()
    
    
    lista_motoboys = Motoboy.objects.filter(loja=loja)

    return render(request, 'relatorio_entregas.html', {
        'vendas': vendas,
        'total_geral': total_geral,
        'quantidade': quantidade,
        'lista_motoboys': lista_motoboys,
        'periodo_selecionado': periodo,
        'motoboy_selecionado': int(motoboy_id) if motoboy_id else None
    })

# --------------------------------- IMPORTÇÃO ---------------------------------

@login_required
def menu_importacao(request):
    form = ImportacaoForm()
    return render(request, 'app_pdv/importacao.html', {'form': form})

@login_required
def importar_clientes(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')

    if request.method == 'POST':
        form = ImportacaoForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = request.FILES['arquivo_excel']
            try:
                df = pd.read_excel(arquivo, engine='openpyxl')
                
                df.columns = (df.columns.str.strip().str.lower()
                              .str.replace('ç', 'c').str.replace('ã', 'a').str.replace('é', 'e'))

                contador_criados = 0
                contador_atualizados = 0

                for index, row in df.iterrows():
                    nome_cliente = row.get('nome')
                    if not nome_cliente: continue

                    endereco = str(row.get('endereco', ''))
                    if endereco == 'nan': endereco = '' 

                    telefone = str(row.get('telefone', ''))
                    if telefone == 'nan': telefone = ''

                    whatsapp = str(row.get('whatsapp', ''))
                    if whatsapp == 'nan': whatsapp = ''

                    obj, created = Cliente.objects.update_or_create(
                        nome=nome_cliente,
                        loja=loja, 
                        defaults={         
                            'endereco': endereco,
                            'telefone': telefone,
                            'whatsapp': whatsapp
                        }
                    )

                    if created:
                        contador_criados += 1
                    else:
                        contador_atualizados += 1
                
                messages.success(request, f"Processo finalizado! {contador_criados} criados e {contador_atualizados} atualizados.")

            except Exception as e:
                messages.error(request, f"Erro ao processar arquivo: {str(e)}")
                
    return redirect('menu_importacao')



@login_required
def importar_produtos(request):
    loja = check_loja(request)
    if not loja: return redirect('admin:index')

    if request.method == 'POST':
        form = ImportacaoForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = request.FILES['arquivo_excel']
            try:
                
                df = pd.read_excel(arquivo, engine='openpyxl')
                
                
                df.columns = df.columns.str.lower().str.strip()
                

                contador = 0
                
                
                def limpar_preco(valor):
                    if pd.isna(valor): return 0.0
                    if isinstance(valor, (int, float)): return float(valor)
                    
                    valor = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
                    try:
                        return float(valor)
                    except:
                        return 0.0

                for index, row in df.iterrows():
                    
                    nome_item = row.get('nome')
                    
                    if nome_item and str(nome_item).lower() != 'nan': 
                        nome_item = str(nome_item).strip()
                        
                        
                        estoque = int(row.get('estoque', 0))
                        custo = limpar_preco(row.get('custo', 0))
                        venda = limpar_preco(row.get('venda', 0))
                        
                        
                        item, created = ItemEstoque.objects.get_or_create(
                            nome=nome_item, 
                            loja=loja
                        )
                        
                        if estoque > 0:
                            item.quantidade_estoque += estoque
                            item.save()

                        
                        nome_venda = nome_item
                        
                        
                        if not Produto.objects.filter(loja=loja, item_estoque=item, nome_venda=nome_venda).exists():
                            Produto.objects.create(
                                loja=loja,
                                item_estoque=item,
                                nome_venda=nome_venda,
                                quantidade_baixa=1,
                                preco_compra=custo,
                                preco_venda=venda
                            )
                            contador += 1
                
                if contador > 0:
                    messages.success(request, f"{contador} produtos importados com sucesso!")
                else:
                    messages.warning(request, "Nenhum produto novo encontrado ou erro nas colunas.")

            except Exception as e:
                
                print(f"ERRO IMPORTAÇÃO: {e}")
                messages.error(request, f"Erro ao processar arquivo: {str(e)}")

    return redirect('menu_importacao') 


#--------------------------------------Vendedor------------------------------------------

@login_required
def cadastrar_vendedor(request):
    
    loja = check_loja(request)
    if request.method == 'POST':
        form = CadastroVendedorForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False 
            user.save()
            
            
            if hasattr(user, 'perfil'):
                user.perfil.loja = loja
                user.perfil.save()

            messages.success(request, f"Vendedor {user.first_name} cadastrado com sucesso!")
            return redirect('lista_vendedores') 
        else:
            messages.error(request, "Erro ao cadastrar. Verifique os dados.")
    else:
        form = CadastroVendedorForm()

    return render(request, 'app_pdv/cadastrar_vendedor.html', {'form': form})

@login_required
def lista_vendedores(request):
    loja = check_loja(request)
    
    vendedores = User.objects.filter(perfil__loja=loja, is_superuser=False).order_by('first_name')
    return render(request, 'app_pdv/lista_vendedores.html', {'vendedores': vendedores})


# ----------------------------- Entregas(MOTOBOY) ----------------------------------------------

@login_required
def lista_entregas(request):
    loja = check_loja(request)
    motoboys = Motoboy.objects.filter(loja=loja).order_by('-ativo', 'nome')
    motos = Moto.objects.filter(loja=loja).order_by('-ativa', 'modelo')
    return render(request, 'app_pdv/entregas.html', {'motoboys': motoboys, 'motos': motos})


@login_required
def cadastrar_motoboy(request):
    loja = check_loja(request)
    
    if request.method == 'POST':
        form = MotoboyForm(request.POST)
        if form.is_valid():
            motoboy = form.save(commit=False)
            motoboy.loja = loja 
            
            cpf_limpo = ''.join(filter(str.isdigit, motoboy.cpf))
            
            if User.objects.filter(username=cpf_limpo).exists():
                # Adiciona erro ao form para aparecer no HTML
                form.add_error('cpf', "Já existe um usuário com este CPF.")
                return render(request, 'app_pdv/cadastrar_motoboy.html', {'form': form})
            
            # 1. Cria o Usuário (Isso dispara o sinal no models.py que cria o PerfilUsuario vazio)
            novo_user = User.objects.create_user(
                username=cpf_limpo, 
                password=cpf_limpo,
                first_name=motoboy.nome.split()[0]
            )
            
            # 2. Grupo de Segurança
            grupo_entregadores, created = Group.objects.get_or_create(name='Entregadores')
            novo_user.groups.add(grupo_entregadores)
            
            # 3. Atualiza o PerfilUsuario com a Loja (O perfil já foi criado pelo sinal)
            perfil, criado = PerfilUsuario.objects.get_or_create(user=novo_user)
            perfil.loja = loja
            perfil.save()

            # 4. Vincula e Salva o Motoboy
            motoboy.user = novo_user
            motoboy.save()
            
            messages.success(request, f"Motoboy cadastrado! Login: {cpf_limpo}")
            return redirect('lista_entregas')
    else:
        form = MotoboyForm()
    
    return render(request, 'app_pdv/cadastrar_motoboy.html', {'form': form, 'titulo': 'Novo Entregador'})

@login_required
def cadastrar_moto(request):
    loja = check_loja(request)
    if request.method == 'POST':
        form = MotoForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.loja = loja
            obj.save()
            messages.success(request, "Moto cadastrada com sucesso!")
            return redirect('lista_entregas')
    else:
        form = MotoForm()
    return render(request, 'app_pdv/cadastrar_moto.html', {'form': form, 'titulo': 'Nova Motocicleta'})

@login_required
def confirmar_recebimento_motoboy(request, venda_id):
    loja = check_loja(request)
    venda = get_object_or_404(Venda, id=venda_id, loja=loja)
    
    if venda.forma_pagamento == 'Dinheiro' and not venda.conferencia_ok:
        venda.conferencia_ok = True
        venda.save()
       
    return redirect('lista_vendas')

# --------------------------------Area do Motoboy (APP FLUTTER)----------------------------------------------




def get_loja_api(user):
    return get_loja_usuario(user)


def get_loja_contexto(request):
    
    loja_id_app = request.GET.get('loja_id')
    
    if loja_id_app:
        try:
            
            return Loja.objects.get(id=loja_id_app)
        except Loja.DoesNotExist:
            pass
            
    
    return get_loja_api(request.user)


class EntregasDisponiveisView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            loja = get_loja_contexto(request) 
            if not loja: 
                return Response({'erro': 'Loja não identificada'}, status=403)

            
            vendas = Venda.objects.filter(
                loja=loja, 
                eh_entrega=True, 
                entregador__isnull=True, 
                status_entrega='PENDENTE' 
            ).filter(
                
                Q(status='EM_SEPARACAO') | Q(status='EM_PREPARACAO')
            ).order_by('-data_venda')
            
            dados = []
            for v in vendas:
                link_zap = None
                if v.cliente and v.cliente.telefone:
                    apenas_numeros = ''.join(filter(str.isdigit, str(v.cliente.telefone)))
                    if apenas_numeros:
                        link_zap = f"https://wa.me/55{apenas_numeros}"

                lista_itens = []
                if hasattr(v, 'itens'):
                    lista_itens = [f"{i.quantidade}x {i.produto.nome_venda}" for i in v.itens.all()]
                else:
                    lista_itens = ["Ver detalhes"]

                dados.append({
                    'id': v.id,
                    'cliente': "Cliente Avulso" if not v.cliente else v.cliente.nome,
                    'endereco': v.endereco_entrega or "Endereço não informado",
                    'valor': float(v.total),
                    'taxa': float(v.taxa_entrega),
                    'itens': lista_itens, 
                    'pagamento': v.forma_pagamento,
                    'troco_para': float(v.troco_para or 0),
                    'whatsapp_link': link_zap,
                    'status_texto': v.status
                })
                
            return Response(dados)
        except Exception as e:
            return Response([], status=200)

class AssumirEntregaView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, venda_id):
        loja = get_loja_contexto(request) 
        try:
            venda = Venda.objects.get(id=venda_id, loja=loja)
            
            if venda.entregador is not None:
                return Response({'erro': 'Entrega já assumida!'}, status=400)
            
            venda.entregador = request.user
            
            
            venda.status_entrega = 'EM_ROTA' 
            
            
            venda.status = 'SAIU_ENTREGA' 
            
            venda.save()
            return Response({'mensagem': 'Boa viagem!'})
            
        except Venda.DoesNotExist:
            return Response({'erro': 'Venda não encontrada'}, status=404)

import logging
logger = logging.getLogger(__name__)

class MinhasEntregasView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            loja = get_loja_contexto(request) 
            if not loja: return Response({'erro': 'Loja erro'}, status=403)

            vendas = Venda.objects.filter(entregador=request.user, loja=loja).order_by('-data_venda')
            
            dados = []
            for v in vendas:
                link_zap = None
                if v.cliente and v.cliente.telefone:
                    apenas_numeros = ''.join(filter(str.isdigit, str(v.cliente.telefone)))
                    if apenas_numeros:
                        link_zap = f"https://wa.me/55{apenas_numeros}"

                lista_itens = []
                if hasattr(v, 'itens'):
                    lista_itens = [f"{i.quantidade}x {i.produto.nome_venda}" for i in v.itens.all()]

                dados.append({
                    'id': v.id,
                    'cliente': v.cliente.nome if v.cliente else "Avulso", 
                    'endereco': v.endereco_entrega,
                    'status': v.status_entrega, 
                    'valor_recebido': float(v.taxa_entrega),
                    'data': v.data_venda.strftime('%d/%m/%Y %H:%M'),
                    'whatsapp_link': link_zap,
                    'pagamento': v.forma_pagamento,
                    'troco_para': float(v.troco_para or 0),
                    'valor': float(v.total), 
                    'itens': lista_itens
                })
                
            return Response(dados)
        except Exception as e:
            return Response({'erro': str(e)}, status=500)
    
def nao_eh_motoboy(user):
    eh_entregador = user.groups.filter(name='Entregadores').exists()
    return not eh_entregador


# ------------------------- ÁREA DA API (DEMAIS ENDPOINTS) ----------------------------

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'nome': user.first_name or user.username,
            'is_superuser': user.is_superuser, 
        })
    

@api_view(['GET'])
@authentication_classes([TokenAuthentication]) 
@permission_classes([IsAuthenticated])
def api_listar_entregas(request):
    """
    Função legada ou secundária. 
    Se o app usar EntregasDisponiveisView, essa aqui pode ficar como backup.
    """
    loja = get_loja_contexto(request) 
    if not loja: return Response([])

    entregas = Venda.objects.filter(
        loja=loja,
        eh_entrega=True, 
        entregador=None
    ).filter(
        Q(status='EM_PREPARACAO') | Q(status='ABERTO') | Q(status='PENDENTE')
    ).order_by('-id')
    
    return Response(gerar_lista_dados(entregas))

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_minhas_entregas(request):
    """
    Função legada ou secundária. 
    O app principal agora usa MinhasEntregasView (classe).
    """
    loja = get_loja_contexto(request) 
    minhas = Venda.objects.filter(entregador=request.user, loja=loja).order_by('-id')
    return Response(gerar_lista_dados(minhas))

# ----------------------- FUNÇÃO AJUDANTE ----------------------------------

def gerar_lista_dados(vendas_queryset):
    lista_dados = []
    for venda in vendas_queryset:
        itens_formatados = []
        try:
            for i in venda.itens.all():
                itens_formatados.append(f"{i.quantidade}x {i.produto.nome_venda}")
        except:
            itens_formatados = ["Erro ao Ler Itens"]
        
        if not itens_formatados:
            itens_formatados = ["Sem itens registrados"]

        link_zap = None
        telefone_visual = "Sem telefone"
        
        if venda.cliente and venda.cliente.telefone:
            telefone_bruto = str(venda.cliente.telefone)
            telefone_visual = telefone_bruto
            apenas_numeros = ''.join(filter(str.isdigit, telefone_bruto))
            if apenas_numeros:
                link_zap = f"https://wa.me/55{apenas_numeros}"

        endereco_final = venda.endereco_entrega
        if not endereco_final and venda.cliente:
            endereco_final = venda.cliente.endereco

        lista_dados.append({
            'id': venda.id,
            'cliente': venda.cliente.nome if venda.cliente else "Cliente Avulso",
            'endereco': endereco_final or "Endereço não informado",
            'valor': float(venda.total),
            'itens': itens_formatados,
            'status': venda.status_entrega,
            'pagamento': venda.forma_pagamento, 
            'whatsapp_link': link_zap,
            'telefone_texto': telefone_visual,
            'troco_para': float(venda.troco_para or 0)
        })
    return lista_dados    
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication]) 
@permission_classes([IsAuthenticated])
def api_assumir_entrega(request, venda_id):
    """
    Função usada nas URLs antigas. Se o urls.py apontar para AssumirEntregaView.as_view(),
    esta função não será chamada, mas mantemos atualizada por segurança.
    """
    loja = get_loja_contexto(request) 
    try:
        venda = Venda.objects.get(id=venda_id, loja=loja)
    except Venda.DoesNotExist:
        return Response({'erro': 'Venda não encontrada'}, status=404)

    if venda.status == 'CANCELADO':
        return Response({'erro': 'Ops! A loja cancelou este pedido.'}, status=400)
    
    if venda.entregador is not None:
        return Response({'erro': 'Esta entrega já foi pega por outro motoboy!'}, status=400)

    venda.entregador = request.user
    venda.status_entrega = 'EM_ROTA'   
    venda.status = 'SAIU_ENTREGA'      
    venda.save()
    
    return Response({'sucesso': 'Entrega aceita! Boa corrida.'})  
    

@api_view(['POST'])
@authentication_classes([TokenAuthentication]) 
@permission_classes([IsAuthenticated])
def api_finalizar_entrega(request, venda_id):
    
    loja = get_loja_contexto(request) 
    try:
        venda = Venda.objects.get(id=venda_id, loja=loja)
    except Venda.DoesNotExist:
        return Response({'erro': 'Venda não encontrada'}, status=404)

    
    if venda.entregador != request.user:
        return Response({'erro': 'Você não é o dono desta entrega!'}, status=403)
    
    venda.status_entrega = 'ENTREGUE' 
    venda.status = 'FINALIZADO'  
    venda.save()
    
    return Response({'sucesso': 'Entrega finalizada com sucesso!'})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_meus_ganhos(request):
    
    loja = get_loja_contexto(request) 
    periodo = request.GET.get('periodo', 'hoje') 
    data_inicio_str = request.GET.get('inicio')
    data_fim_str = request.GET.get('fim')

    hoje = date.today()
    filtro_data = {}

    if periodo == 'hoje':
        filtro_data['data_venda__date'] = hoje
    elif periodo == 'semana':
        inicio_semana = hoje - timedelta(days=hoje.weekday()) 
        filtro_data['data_venda__date__gte'] = inicio_semana
    elif periodo == 'mes':
        filtro_data['data_venda__month'] = hoje.month
        filtro_data['data_venda__year'] = hoje.year
    elif periodo == 'intervalo' and data_inicio_str and data_fim_str:
        try:
            dt_ini = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            dt_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            filtro_data['data_venda__date__range'] = [dt_ini, dt_fim]
        except:
            return Response({'erro': 'Formato de data inválido'}, status=400)

    vendas = Venda.objects.filter(
        loja=loja,
        entregador=request.user, 
        status_entrega='ENTREGUE', 
        **filtro_data
    ).order_by('-id')

    total_ganho = sum(v.taxa_entrega for v in vendas)
    quantidade = vendas.count()

    historico = []
    for v in vendas:
        historico.append({
            'data': v.data_venda.strftime('%d/%m/%Y'),
            'cliente': v.cliente.nome if v.cliente else 'Avulso',
            'valor': float(v.taxa_entrega)
        })

    return Response({
        'total': float(total_ganho),
        'quantidade': quantidade,
        'historico': historico
    })

# -------------------------------- APP DO CLIENTE & TORRE ----------------------------

@login_required
def torre_controle(request):
    return render(request, 'app_pdv/torre_controle.html')


@login_required
def api_pedidos_torre(request):
    loja = check_loja(request)
    if not loja: return JsonResponse({'erro': 'Sem loja'}, status=403)

    
    pedidos = Venda.objects.filter(
        loja=loja,
        status__in=['PENDENTE', 'EM_PREPARACAO', 'SAIU_ENTREGA']
    ).order_by('data_venda') 

    lista_pedidos = []
    tem_novo_pedido = False

    for venda in pedidos:
        if venda.status == 'PENDENTE':
            tem_novo_pedido = True

        lista_pedidos.append({
            'id': venda.id,
            'cliente': venda.cliente.nome if venda.cliente else 'Cliente App',
            'total': float(venda.total),
            'status': venda.status,
            'origem': venda.origem,
            'itens': [f"{item.quantidade}x {item.produto.nome_venda}" for item in venda.itens.all()],
            'endereco': venda.endereco_entrega,
            'pagamento': venda.forma_pagamento,
            'obs': venda.observacao or ""
        })

    return JsonResponse({
        'pedidos': lista_pedidos,
        'tocar_som': tem_novo_pedido
    })


@csrf_exempt
@login_required
def api_atualizar_status_pedido(request, venda_id):
    loja = check_loja(request)
    if request.method == 'POST':
        data = json.loads(request.body)
        novo_status = data.get('novo_status')
        
        venda = get_object_or_404(Venda, id=venda_id, loja=loja)
        venda.status = novo_status
        venda.save()
        
        return JsonResponse({'sucesso': True})
    return JsonResponse({'erro': 'Método inválido'}, status=400)

def api_listar_produtos(request):
    
    
    loja_id = request.GET.get('loja_id', 1) 
    produtos = Produto.objects.filter(loja_id=loja_id, item_estoque__quantidade_estoque__gt=0, ativo=True)
    serializer = ProdutoCatalogoSerializer(produtos, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
@transaction.atomic
def api_criar_pedido(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            
            loja_id = data.get('loja_id', 1) 
            loja = Loja.objects.get(id=loja_id)

            cliente_nome = data.get('cliente_nome', 'Cliente App')
            telefone = data.get('telefone', '')
            endereco_novo = data.get('endereco', '')
            observacao_texto = data.get('obs', '')
            
            
            valor_troco = 0.00
            if 'Troco p/:' in observacao_texto:
                try:
                    partes = observacao_texto.split('R$')
                    if len(partes) > 1:
                        valor_limpo = partes[1].replace(')', '').strip()
                        valor_troco = float(valor_limpo)
                except:
                    valor_troco = 0.00


            

            if not loja.loja_aberta:
                return JsonResponse({
                    'erro': 'LOJA FECHADA - PEDIDO REJEITADO'
                }, status=403)

            
            cliente_obj = None
            if telefone:
                
                cliente_obj, created = Cliente.objects.get_or_create(
                    telefone=telefone, 
                    loja=loja,
                    defaults={
                        'nome': cliente_nome,
                        'endereco': endereco_novo
                    }
                )
                if not created:
                    cliente_obj.nome = cliente_nome
                    cliente_obj.endereco = endereco_novo
                    cliente_obj.save()

            
            venda = Venda.objects.create(
                loja=loja, 
                cliente=cliente_obj,
                total=data.get('total'),
                eh_entrega=True,
                taxa_entrega=data.get('taxa_entrega', 0.0),
                endereco_entrega=endereco_novo,
                forma_pagamento=data.get('pagamento'),
                observacao=observacao_texto,
                origem='APP',
                status='PENDENTE',
                troco_para=valor_troco 
            )

            
            itens_data = data.get('itens', [])
            for item in itens_data:
                produto = Produto.objects.get(id=item['id_produto'], loja=loja)
                ItemVenda.objects.create(
                    venda=venda,
                    produto=produto,
                    quantidade=item['quantidade'],
                    preco_unitario=produto.preco_venda
                )

            return JsonResponse({'sucesso': True, 'pedido_id': venda.id}, status=201)

        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)
            
    return JsonResponse({'erro': 'Método inválido'}, status=405)



def api_buscar_cliente(request):
    telefone = request.GET.get('telefone')
    loja_id = request.GET.get('loja_id', 1)

    if telefone:
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        cliente = Cliente.objects.filter(telefone=telefone, loja_id=loja_id).first()
        
        if cliente:
            return JsonResponse({
                'encontrou': True,
                'nome': cliente.nome,
                'endereco': cliente.endereco,
                'telefone': cliente.telefone
            })
            
    return JsonResponse({'encontrou': False})


def api_meus_pedidos(request):
    telefone = request.GET.get('telefone')
    loja_id = request.GET.get('loja_id', 1)

    if not telefone: return JsonResponse([], safe=False)

    vendas = Venda.objects.filter(cliente__telefone=telefone, loja_id=loja_id).order_by('-id')
    
    lista_pedidos = []
    for venda in vendas:
        itens_desc = []
        for item in venda.itens.all():
            itens_desc.append(f"{item.quantidade}x {item.produto.nome_venda}")
            
        lista_pedidos.append({
            'id': venda.id,
            'data': venda.data_venda.strftime('%d/%m/%Y %H:%M'),
            'total': float(venda.total),
            'status': venda.get_status_display(),
            'itens': itens_desc,
            'cor_status': venda.status 
        })
        
    return JsonResponse(lista_pedidos, safe=False)


@login_required
def api_conferir_venda(request, venda_id):
    loja = check_loja(request)
    if request.method == 'POST':
        venda = get_object_or_404(Venda, id=venda_id, loja=loja)
        venda.conferencia_ok = True
        venda.save()
        return JsonResponse({'sucesso': True})
    return JsonResponse({'sucesso': False, 'erro': 'Método inválido'})


def api_obter_taxa_entrega(request):
    
    loja_id = request.GET.get('loja_id', 1)
    loja = Loja.objects.filter(id=loja_id).first()
    taxa = float(loja.taxa_entrega_app) if loja else 5.00
    return JsonResponse({'taxa': taxa})


@login_required
@csrf_exempt
def definir_taxa_entrega(request):
    loja = check_loja(request)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nova_taxa = float(data.get('nova_taxa'))
            
            loja.taxa_entrega_app = nova_taxa
            loja.save()
            
            return JsonResponse({'sucesso': True})
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)
    return JsonResponse({'erro': 'Método inválido'}, status=400)


@csrf_exempt
@login_required
def api_toggle_loja(request):
    """
    Liga ou Desliga a loja.
    Chamado pelo botão na Torre de Controle.
    """
    loja = check_loja(request) 
    if not loja: 
        return JsonResponse({'erro': 'Loja não encontrada'}, status=403)
    
    if request.method == 'POST':
        
        loja.loja_aberta = not loja.loja_aberta
        loja.save()
        
        status_texto = "ABERTA" if loja.loja_aberta else "FECHADA"
        return JsonResponse({
            'sucesso': True, 
            'loja_aberta': loja.loja_aberta, 
            'msg': f'Sucesso! A loja agora está {status_texto}.'
        })
        
    
    return JsonResponse({'loja_aberta': loja.loja_aberta})