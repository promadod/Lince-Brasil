"""Filtros do histórico de vendas (/vendas/historico/)."""
from decimal import Decimal, InvalidOperation

from django.db.models import Q

from .models import ORIGEM_VENDA_CHOICES, MEIO_LIQUIDACAO_VENDA_CHOICES

FILTROS_STATUS_HISTORICO = [
    ('', 'Todos os status'),
    ('VENDA_NA_LOJA', 'Venda na loja (PDV)'),
    ('RETIRADA_APP', 'Retirada na loja (App)'),
    ('CANCELADO', 'Cancelada'),
    ('AGUARDANDO_MOTOBOY', 'Aguardando motoboy'),
    ('EM_ROTA', 'Em rota'),
    ('ENTREGA_FINALIZADA', 'Entrega finalizada'),
    ('FIADO', 'Fiado'),
    ('AGUARDANDO_FINALIZAR', 'Aguardando finalizar'),
    ('ABERTO', 'Em aberto'),
    ('ORCAMENTO', 'Orçamento'),
    ('EM_PREPARACAO', 'Em separação'),
    ('SAIU_ENTREGA', 'Saiu para entrega'),
    ('FINALIZADO', 'Finalizado (geral)'),
    ('PENDENTE', 'Aguardando aprovação'),
]

_MAPA_STATUS = {
    'VENDA_NA_LOJA': Q(status='FINALIZADO', origem='PDV', eh_entrega=False),
    'RETIRADA_APP': Q(status='FINALIZADO', origem='APP', eh_entrega=False),
    'CANCELADO': Q(status='CANCELADO'),
    'AGUARDANDO_MOTOBOY': Q(eh_entrega=True, status_entrega='PENDENTE'),
    'EM_ROTA': Q(eh_entrega=True, status_entrega='EM_ROTA'),
    'ENTREGA_FINALIZADA': Q(eh_entrega=True, status_entrega='ENTREGUE'),
    'FIADO': Q(status='FIADO'),
    'AGUARDANDO_FINALIZAR': Q(status='AGUARDANDO_FINALIZAR'),
    'ABERTO': Q(status='ABERTO'),
    'ORCAMENTO': Q(status='ORCAMENTO'),
    'EM_PREPARACAO': Q(status='EM_PREPARACAO'),
    'SAIU_ENTREGA': Q(status='SAIU_ENTREGA'),
    'FINALIZADO': Q(status='FINALIZADO'),
    'PENDENTE': Q(status='PENDENTE'),
}


def aplicar_filtro_status_vendas(queryset, status_filtro):
    if not status_filtro:
        return queryset
    filtro = _MAPA_STATUS.get(status_filtro)
    if filtro is not None:
        return queryset.filter(filtro)
    return queryset.filter(status=status_filtro)


def filtrar_vendas_historico(queryset, get_params):
    """Aplica filtros GET ao queryset de vendas."""
    data_inicio = (get_params.get('data_inicio') or '').strip()
    data_fim = (get_params.get('data_fim') or '').strip()
    status_filtro = (get_params.get('filtro_status') or get_params.get('status') or '').strip()
    origem = (get_params.get('origem') or '').strip()
    venda_id = (get_params.get('venda_id') or '').strip().lstrip('#')
    valor_str = (get_params.get('valor') or '').strip()
    cliente = (get_params.get('cliente') or '').strip()
    meio_liquidacao = (get_params.get('meio_liquidacao') or '').strip()
    forma_pagamento = (get_params.get('forma_pagamento') or '').strip()

    if data_inicio:
        queryset = queryset.filter(data_venda__date__gte=data_inicio)
    if data_fim:
        queryset = queryset.filter(data_venda__date__lte=data_fim)
    if origem in dict(ORIGEM_VENDA_CHOICES):
        queryset = queryset.filter(origem=origem)
    if venda_id:
        try:
            queryset = queryset.filter(id=int(venda_id))
        except ValueError:
            pass
    if valor_str:
        try:
            valor_dec = Decimal(valor_str.replace(',', '.'))
            queryset = queryset.filter(total=valor_dec)
        except (InvalidOperation, ValueError):
            pass
    if cliente:
        queryset = queryset.filter(cliente__nome__icontains=cliente)
    if meio_liquidacao:
        codigos_validos = {c for c, _ in MEIO_LIQUIDACAO_VENDA_CHOICES}
        if meio_liquidacao in codigos_validos:
            queryset = queryset.filter(
                Q(meio_liquidacao=meio_liquidacao)
                | Q(liquidacoes__meio_liquidacao=meio_liquidacao)
            ).distinct()
    if forma_pagamento:
        queryset = queryset.filter(forma_pagamento=forma_pagamento)

    queryset = aplicar_filtro_status_vendas(queryset, status_filtro)

    filtros = {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'filtro_status': status_filtro,
        'origem': origem,
        'venda_id': venda_id,
        'valor': valor_str,
        'cliente': cliente,
        'meio_liquidacao': meio_liquidacao,
        'forma_pagamento': forma_pagamento,
    }
    filtros_ativos = any(filtros.values())
    return queryset, filtros, filtros_ativos
