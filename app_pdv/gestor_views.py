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
