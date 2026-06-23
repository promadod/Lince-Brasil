"""Estatísticas e campanhas de clientes por bairro."""
from datetime import timedelta

from django.db.models import Max, Count, Q
from django.utils import timezone

from .models import Cliente, Venda
from .whatsapp_service import gerar_link_whatsapp


def _ultima_compra_map(loja_ids):
    return {
        row['cliente_id']: row['ultima']
        for row in Venda.objects.filter(
            loja_id__in=loja_ids,
            status='FINALIZADO',
            cliente__isnull=False,
        )
        .values('cliente_id')
        .annotate(ultima=Max('data_venda__date'))
    }


def montar_estatisticas_clientes(lojas_alvo):
    hoje = timezone.localdate()
    limite_ativo = hoje - timedelta(days=30)
    limite_inativo = hoje - timedelta(days=60)
    loja_ids = list(lojas_alvo.values_list('id', flat=True))

    clientes = Cliente.objects.filter(loja_id__in=loja_ids).order_by('nome')
    ultimas = _ultima_compra_map(loja_ids)

    total = clientes.count()
    ativos = 0
    inativos = 0
    por_bairro = {}

    for c in clientes:
        ultima = ultimas.get(c.id)
        bairro = (c.bairro or 'Sem bairro').strip() or 'Sem bairro'
        if bairro not in por_bairro:
            por_bairro[bairro] = {'total': 0, 'ativos': 0, 'inativos': 0, 'clientes': []}

        status = 'novo'
        if ultima:
            if ultima >= limite_ativo:
                ativos += 1
                status = 'ativo'
                por_bairro[bairro]['ativos'] += 1
            elif ultima < limite_inativo:
                inativos += 1
                status = 'inativo'
                por_bairro[bairro]['inativos'] += 1
            else:
                status = 'regular'

        por_bairro[bairro]['total'] += 1
        por_bairro[bairro]['clientes'].append({
            'id': c.id,
            'nome': c.nome,
            'telefone': c.telefone or '',
            'whatsapp': c.whatsapp or c.telefone or '',
            'bairro': bairro,
            'endereco': c.endereco or '',
            'ultima_compra': ultima.strftime('%d/%m/%Y') if ultima else None,
            'status': status,
            'pontos_fidelidade': float(c.pontos_fidelidade or 0),
            'promocao_fidelidade': c.promocao_fidelidade_ativa,
        })

    bairros_ordenados = sorted(
        [
            {
                'bairro': nome,
                'total': dados['total'],
                'ativos': dados['ativos'],
                'inativos': dados['inativos'],
                'clientes': dados['clientes'],
            }
            for nome, dados in por_bairro.items()
        ],
        key=lambda x: (-x['total'], x['bairro']),
    )

    return {
        'total': total,
        'ativos_30d': ativos,
        'inativos_60d': inativos,
        'por_bairro': bairros_ordenados,
    }


def montar_links_campanha(loja, publico='ativos', desconto_pct=None):
    """Gera links WhatsApp para campanha de desconto."""
    hoje = timezone.localdate()
    limite_ativo = hoje - timedelta(days=30)
    limite_inativo = hoje - timedelta(days=60)
    desconto = desconto_pct if desconto_pct is not None else float(loja.campanha_desconto_pct or 10)

    if publico == 'ativos':
        template = loja.msg_campanha_ativos or (
            'Olá {cliente}! Temos {desconto}% de desconto especial para você. '
            'Peça pelo app ou WhatsApp!'
        )
    else:
        template = loja.msg_campanha_inativos or (
            'Olá {cliente}! Sentimos sua falta. {desconto}% OFF nos produtos — '
            'volte a comprar conosco!'
        )

    ultimas = _ultima_compra_map([loja.id])
    clientes = Cliente.objects.filter(loja=loja)
    links = []

    for c in clientes:
        ultima = ultimas.get(c.id)
        if publico == 'ativos':
            if not ultima or ultima < limite_ativo:
                continue
        else:
            if ultima and ultima >= limite_inativo:
                continue

        tel = c.whatsapp or c.telefone
        if not tel:
            continue
        msg = (
            template.replace('{cliente}', c.nome)
            .replace('{bairro}', c.bairro or '')
            .replace('{desconto}', str(desconto))
        )
        links.append({
            'cliente_id': c.id,
            'nome': c.nome,
            'bairro': c.bairro or '—',
            'whatsapp_link': gerar_link_whatsapp(tel, msg),
        })

    return links
