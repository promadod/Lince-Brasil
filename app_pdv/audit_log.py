"""Registro de auditoria — ações dos usuários no sistema."""
from .models import LogAuditoria
from .seguranca import obter_ip_cliente


def registrar_log(request, acao, descricao, modelo='', objeto_id=None, loja=None):
    if not request or not getattr(request, 'user', None) or not request.user.is_authenticated:
        return
    usuario = request.user
    if loja is None:
        perfil = getattr(usuario, 'perfil', None)
        loja = perfil.loja if perfil else None
    LogAuditoria.objects.create(
        usuario=usuario,
        loja=loja,
        acao=acao,
        modelo=modelo or '',
        objeto_id=objeto_id,
        descricao=descricao[:2000],
        ip=obter_ip_cliente(request) or None,
    )
