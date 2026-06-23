from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .gestor_api import (
    GestorAcessoNegado,
    usuario_pode_acessar_gestor,
    lojas_permitidas_gestor,
    montar_lista_lojas,
    montar_resumo_gestor,
    montar_financeiro,
    montar_vendas_gestor,
    resolver_lojas_alvo,
    parse_periodo,
)
from .clientes_service import montar_estatisticas_clientes, montar_links_campanha


def _params_gestor(request):
    return {
        'loja_id': request.GET.get('loja_id', 'todas'),
        'periodo': request.GET.get('periodo', 'hoje'),
        'data_inicio': request.GET.get('data_inicio'),
        'data_fim': request.GET.get('data_fim'),
    }


def _handle_gestor_error(exc):
    if isinstance(exc, GestorAcessoNegado):
        return Response({'erro': str(exc)}, status=status.HTTP_403_FORBIDDEN)
    if isinstance(exc, ValueError):
        return Response({'erro': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    raise exc


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_gestor_resumo(request):
    if not usuario_pode_acessar_gestor(request.user):
        return Response(
            {'erro': 'Sem permissão para o painel gestor.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    p = _params_gestor(request)
    try:
        data = montar_resumo_gestor(
            request.user,
            loja_id_param=p['loja_id'],
            periodo=p['periodo'],
            data_inicio=p['data_inicio'],
            data_fim=p['data_fim'],
        )
        return Response(data)
    except (GestorAcessoNegado, ValueError) as exc:
        return _handle_gestor_error(exc)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_gestor_lojas(request):
    if not usuario_pode_acessar_gestor(request.user):
        return Response(
            {'erro': 'Sem permissão para o painel gestor.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    lojas = lojas_permitidas_gestor(request.user)
    return Response({'lojas': montar_lista_lojas(lojas)})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_gestor_financeiro(request):
    if not usuario_pode_acessar_gestor(request.user):
        return Response(
            {'erro': 'Sem permissão para o painel gestor.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    p = _params_gestor(request)
    try:
        lojas_alvo, loja_id_resolvido = resolver_lojas_alvo(request.user, p['loja_id'])
        data_ini, data_fim_res, periodo_res = parse_periodo(
            p['periodo'], p['data_inicio'], p['data_fim']
        )
        return Response({
            'periodo': periodo_res,
            'data_inicio': data_ini.isoformat(),
            'data_fim': data_fim_res.isoformat(),
            'loja_id': loja_id_resolvido,
            'financeiro': montar_financeiro(lojas_alvo, data_ini, data_fim_res),
        })
    except (GestorAcessoNegado, ValueError) as exc:
        return _handle_gestor_error(exc)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_gestor_vendas(request):
    if not usuario_pode_acessar_gestor(request.user):
        return Response(
            {'erro': 'Sem permissão para o painel gestor.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    p = _params_gestor(request)
    try:
        limite = min(int(request.GET.get('limite', 50)), 100)
    except (TypeError, ValueError):
        limite = 50
    try:
        data = montar_vendas_gestor(
            request.user,
            loja_id_param=p['loja_id'],
            periodo=p['periodo'],
            data_inicio=p['data_inicio'],
            data_fim=p['data_fim'],
            limite=limite,
        )
        return Response(data)
    except (GestorAcessoNegado, ValueError) as exc:
        return _handle_gestor_error(exc)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_gestor_clientes(request):
    if not usuario_pode_acessar_gestor(request.user):
        return Response(
            {'erro': 'Sem permissão para o painel gestor.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    p = _params_gestor(request)
    try:
        lojas_alvo, loja_id_resolvido = resolver_lojas_alvo(request.user, p['loja_id'])
        stats = montar_estatisticas_clientes(lojas_alvo)
        stats['loja_id'] = loja_id_resolvido
        return Response(stats)
    except (GestorAcessoNegado, ValueError) as exc:
        return _handle_gestor_error(exc)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_gestor_campanha(request):
    if not usuario_pode_acessar_gestor(request.user):
        return Response(
            {'erro': 'Sem permissão para o painel gestor.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    publico = request.GET.get('publico', 'ativos')
    if publico not in ('ativos', 'inativos'):
        return Response({'erro': 'publico deve ser ativos ou inativos'}, status=400)
    try:
        lojas_alvo, loja_id_resolvido = resolver_lojas_alvo(
            request.user, request.GET.get('loja_id', 'todas')
        )
        if lojas_alvo.count() != 1:
            return Response({'erro': 'Selecione uma loja específica para campanha.'}, status=400)
        loja = lojas_alvo.first()
        desconto = request.GET.get('desconto')
        desconto_val = float(desconto) if desconto else None
        links = montar_links_campanha(loja, publico=publico, desconto_pct=desconto_val)
        return Response({
            'loja_id': loja_id_resolvido,
            'publico': publico,
            'desconto': desconto_val or float(loja.campanha_desconto_pct or 10),
            'links': links,
        })
    except (GestorAcessoNegado, ValueError) as exc:
        return _handle_gestor_error(exc)
