from django.contrib.auth.views import LoginView
from django.contrib import messages

from .seguranca import (
    conta_congelada_username,
    ip_bloqueado,
    minutos_restantes_bloqueio_ip,
    obter_ip_cliente,
    usuario_eh_superuser,
)


class SegurancaLoginView(LoginView):
    template_name = 'registration/login.html'

    def post(self, request, *args, **kwargs):
        username = (request.POST.get('username') or '').strip()
        if not usuario_eh_superuser(username):
            ip = obter_ip_cliente(request)
            if ip_bloqueado(ip):
                mins = minutos_restantes_bloqueio_ip(ip)
                messages.error(
                    request,
                    f'Muitas tentativas de login. IP bloqueado por {mins} minuto(s).',
                )
                return self.get(request)
            if conta_congelada_username(username):
                messages.error(
                    request,
                    'Conta congelada. Solicite ao administrador do sistema.',
                )
                return self.get(request)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        username = (self.request.POST.get('username') or '').strip()
        if not usuario_eh_superuser(username):
            messages.error(self.request, 'Usuário ou senha incorretos.')
        return super().form_invalid(form)
