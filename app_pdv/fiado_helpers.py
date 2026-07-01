"""Helpers compartilhados entre relatórios fiado e agendamento de parcelas."""
from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from .models import ParcelaFiadoAgendada, Venda, saldo_agendavel_venda, total_parcelas_agendadas_venda


def formatar_itens_venda(venda):
    partes = []
    for item in venda.itens.select_related('produto__item_estoque').all():
        qtd = item.quantidade
        unidade = item.produto.item_estoque.unidade_medida
        if unidade == 'UN':
            qtd_fmt = f"{int(qtd)}"
        else:
            qtd_fmt = f"{qtd:.3f}".rstrip('0').rstrip('.')
        partes.append(f"{qtd_fmt}x {item.produto.nome_venda}")
    return ', '.join(partes) if partes else '—'


def montar_item_venda_fiado(venda, parcelas_qs=None):
    from django.utils.timezone import localtime

    if parcelas_qs is None:
        parcelas_qs = venda.parcelas_fiado_agendadas.all()

    parcelas = []
    tem_atrasada = False
    for p in parcelas_qs:
        atrasada = p.esta_atrasada
        if atrasada:
            tem_atrasada = True
        parcelas.append({
            'id': p.id,
            'valor': p.valor,
            'data_vencimento': p.data_vencimento.strftime('%d/%m/%Y'),
            'data_entrada': localtime(p.data_entrada).strftime('%d/%m/%Y %H:%M'),
            'status': p.status,
            'status_label': p.get_status_display(),
            'atrasada': atrasada,
        })

    saldo = venda.saldo_devedor
    pago = venda.valor_pago_fiado
    agendado = total_parcelas_agendadas_venda(venda)
    agendavel = saldo_agendavel_venda(venda)

    return {
        'venda': venda,
        'venda_id': venda.id,
        'cliente': venda.cliente.nome if venda.cliente else '—',
        'cliente_id': venda.cliente_id,
        'loja': venda.loja.nome,
        'data': localtime(venda.data_venda).strftime('%d/%m/%Y %H:%M'),
        'qtd_total': venda.qtd_itens_vendidos,
        'itens_resumo': formatar_itens_venda(venda),
        'total': venda.total,
        'pago': pago,
        'saldo': saldo,
        'saldo_agendavel': agendavel,
        'total_agendado': agendado,
        'parcelas': parcelas,
        'tem_parcela_atrasada': tem_atrasada,
    }


def listar_vendas_fiado_abertas(lojas_fiado, data_inicio=None, data_fim=None, todas_datas=False):
    qs = Venda.objects.filter(
        loja__in=lojas_fiado,
        eh_fiado=True,
        status='FIADO',
    ).select_related('cliente', 'loja').prefetch_related(
        'itens__produto__item_estoque',
        'parcelas_fiado_agendadas',
    )
    if not todas_datas and data_inicio and data_fim:
        qs = qs.filter(data_venda__date__range=[data_inicio, data_fim])
    qs = qs.order_by('-data_venda')

    lista = []
    total_devedor = Decimal('0')
    total_vendido = Decimal('0')
    total_pago = Decimal('0')

    for venda in qs:
        if venda.saldo_devedor <= 0:
            continue
        item = montar_item_venda_fiado(venda)
        lista.append(item)
        total_devedor += item['saldo']
        total_vendido += Decimal(str(venda.total or 0))
        total_pago += item['pago']

    return lista, {
        'total_devedor': total_devedor,
        'total_vendido': total_vendido,
        'total_pago': total_pago,
        'qtd_vendas': len(lista),
    }


def agrupar_fiado_por_cliente(lista_fiado):
    grupos = defaultdict(list)
    for item in lista_fiado:
        chave = item['cliente_id'] or f"sem_{item['venda_id']}"
        grupos[chave].append(item)

    resultado = []
    for chave, vendas in grupos.items():
        saldo_total = sum(v['saldo'] for v in vendas)
        agendavel_total = sum(v['saldo_agendavel'] for v in vendas)
        tem_atrasada = any(v['tem_parcela_atrasada'] for v in vendas)
        resultado.append({
            'chave': str(chave),
            'cliente': vendas[0]['cliente'],
            'cliente_id': vendas[0]['cliente_id'],
            'qtd_vendas': len(vendas),
            'saldo_total': saldo_total,
            'saldo_agendavel_total': agendavel_total,
            'tem_parcela_atrasada': tem_atrasada,
            'vendas': vendas,
        })
    resultado.sort(key=lambda g: g['cliente'].lower())
    return resultado


def listar_parcelas_agendadas(lojas_fiado, data_inicio, data_fim, status=None):
    from django.utils.timezone import localtime

    qs = ParcelaFiadoAgendada.objects.filter(
        loja__in=lojas_fiado,
        data_vencimento__range=[data_inicio, data_fim],
    ).select_related('venda', 'cliente', 'loja').order_by('data_vencimento', 'cliente__nome')

    if status:
        qs = qs.filter(status=status)

    lista = []
    total_agendado = Decimal('0')
    total_atrasado = Decimal('0')
    hoje = timezone.localdate()

    for p in qs:
        atrasada = p.esta_atrasada
        if p.status == 'AGENDADO':
            total_agendado += p.valor
            if atrasada:
                total_atrasado += p.valor
        lista.append({
            'parcela': p,
            'id': p.id,
            'status': p.status,
            'status_label': p.get_status_display(),
            'venda_id': p.venda_id,
            'cliente': p.cliente.nome,
            'entrada': localtime(p.data_entrada).strftime('%d/%m/%Y %H:%M'),
            'vencimento': p.data_vencimento.strftime('%d/%m/%Y'),
            'valor': p.valor,
            'atrasada': atrasada,
            'loja': p.loja.nome,
        })

    return lista, {
        'qtd': len(lista),
        'total_agendado': total_agendado,
        'total_atrasado': total_atrasado,
    }


def distribuir_pagamento_fiado(vendas_ordenadas, valor_total):
    """Distribui pagamento entre vendas (FIFO). Retorna lista (venda, valor)."""
    restante = Decimal(str(valor_total))
    alocacoes = []
    for venda in vendas_ordenadas:
        if restante <= 0:
            break
        saldo = venda.saldo_devedor
        if saldo <= 0:
            continue
        pago = min(saldo, restante)
        alocacoes.append((venda, pago))
        restante -= pago
    if restante > 0:
        raise ValueError('Valor do pagamento excede o saldo devedor unificado.')
    return alocacoes
