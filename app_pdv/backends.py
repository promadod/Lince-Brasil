from django.contrib.auth.backends import ModelBackend

from .seguranca import conta_congelada_user


class SegurancaAuthBackend(ModelBackend):
    """Bloqueia login de contas congeladas (superusuário isento)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user and conta_congelada_user(user):
            return None
        return user

    def get_user(self, user_id):
        user = super().get_user(user_id)
        if user and conta_congelada_user(user):
            return None
        return user
