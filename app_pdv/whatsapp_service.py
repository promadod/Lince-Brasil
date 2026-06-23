"""Utilitários de WhatsApp — gera links wa.me com mensagens personalizáveis (SaaS)."""
import urllib.parse

from django.utils import timezone

from .models import get_nome_forma_pagamento


def limpar_telefone(numero):
    if not numero:
        return ''
    digits = ''.join(filter(str.isdigit, str(numero)))
    if digits.startswith('55') and len(digits) > 11:
        return digits
    if len(digits) >= 10:
        return f'55{digits}'
    return digits


def gerar_link_whatsapp(numero, mensagem):
    tel = limpar_telefone(numero)
    if not tel or not mensagem:
        return None
    texto = urllib.parse.quote(mensagem.strip())
    return f'https://wa.me/{tel}?text={texto}'


def _formatar_itens_venda(venda):
    partes = []
    for item in venda.itens.select_related('produto').all():
        qtd = item.quantidade
        if item.produto.item_estoque.unidade_medida == 'UN':
            qtd_fmt = f'{int(qtd)}'
        else:
            qtd_fmt = f'{qtd:.3f}'.rstrip('0').rstrip('.')
        partes.append(f'{qtd_fmt}x {item.produto.nome_venda}')
    return '\n'.join(partes) if partes else '—'


def _aplicar_template(template, contexto):
    msg = template or ''
    for chave, valor in contexto.items():
        msg = msg.replace(f'{{{chave}}}', str(valor or ''))
    return msg.strip()


def contexto_pedido(venda):
    cliente = venda.cliente
    return {
        'pedido': venda.id,
        'cliente': cliente.nome if cliente else 'Consumidor',
        'telefone': cliente.telefone if cliente else '',
        'whatsapp': cliente.whatsapp if cliente else '',
        'endereco': venda.endereco_entrega or (cliente.endereco if cliente else ''),
        'pagamento': get_nome_forma_pagamento(venda.loja, venda.forma_pagamento),
        'itens': _formatar_itens_venda(venda),
        'total': f'R$ {float(venda.total or 0):.2f}',
        'obs': venda.observacao or '',
        'data': timezone.localtime(venda.data_venda).strftime('%d/%m/%Y %H:%M'),
    }


def notificar_novo_pedido_empresa(venda):
    """Gera link WhatsApp para a empresa quando um pedido é criado."""
    loja = venda.loja
    if not loja.whatsapp_notificar_pedido or not loja.whatsapp_numero_empresa:
        return None
    template = loja.whatsapp_msg_novo_pedido or (
        '🆕 *Novo Pedido #{pedido}*\n'
        'Cliente: {cliente}\n'
        'WhatsApp: {whatsapp}\n'
        'Endereço: {endereco}\n'
        'Pagamento: {pagamento}\n'
        'Itens:\n{itens}\n'
        'Total: {total}\n'
        'Obs: {obs}'
    )
    msg = _aplicar_template(template, contexto_pedido(venda))
    return gerar_link_whatsapp(loja.whatsapp_numero_empresa, msg)


def notificar_cliente_saiu_entrega(venda):
    loja = venda.loja
    if not venda.cliente:
        return None
    tel = venda.cliente.whatsapp or venda.cliente.telefone
    if not tel:
        return None
    template = loja.whatsapp_msg_saiu_entrega or (
        'Olá {cliente}! Seu pedido #{pedido} saiu para entrega.'
    )
    ctx = contexto_pedido(venda)
    msg = _aplicar_template(template, ctx)
    return gerar_link_whatsapp(tel, msg)


def notificar_cliente_entrega_concluida(venda):
    loja = venda.loja
    if not venda.cliente:
        return None
    tel = venda.cliente.whatsapp or venda.cliente.telefone
    if not tel:
        return None
    template = loja.whatsapp_msg_entrega_concluida or (
        'Olá {cliente}! Seu pedido #{pedido} foi entregue. Obrigado!'
    )
    ctx = contexto_pedido(venda)
    msg = _aplicar_template(template, ctx)
    return gerar_link_whatsapp(tel, msg)
