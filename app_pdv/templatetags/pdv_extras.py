from django import template

from app_pdv.filtros_venda import FILTROS_STATUS_HISTORICO
from app_pdv.models import ORIGEM_VENDA_CHOICES

register = template.Library()


@register.simple_tag
def historico_status_opcoes():
    return FILTROS_STATUS_HISTORICO


@register.simple_tag
def historico_origem_opcoes():
    return ORIGEM_VENDA_CHOICES
