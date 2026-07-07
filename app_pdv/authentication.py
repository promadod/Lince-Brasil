from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .seguranca import conta_congelada_user, token_api_valido


class SessaoUnicaTokenAuthentication(TokenAuthentication):
    """
    Token DRF com sessão única: novo login invalida token anterior.
    Superusuário isento. Endpoints AllowAny não passam por aqui.
    """

    keyword = 'Token'

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if user.is_superuser:
            return user, token
        if conta_congelada_user(user):
            raise AuthenticationFailed(
                'Conta congelada. Solicite ao administrador do sistema.'
            )
        if not token_api_valido(user, key):
            raise AuthenticationFailed(
                'Sessão encerrada: login realizado em outro dispositivo.'
            )
        return user, token
