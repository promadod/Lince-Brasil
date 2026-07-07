from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from .models import Loja
from .seguranca import (
    conta_congelada_username,
    ip_bloqueado,
    minutos_restantes_bloqueio_ip,
    obter_ip_cliente,
    usuario_eh_superuser,
)


class BloqueioPagamentoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Se não estiver logado, libera
        if not request.user.is_authenticated:
            return self.get_response(request)

        # 2. Se for Superuser, libera
        if request.user.is_superuser:
            return self.get_response(request)

        # 3. URLs liberadas
        urls_liberadas = [
            reverse('logout'),
            reverse('assinatura_bloqueada'),
            '/admin/', 
            '/static/',
            '/media/',
            '/api/', 
        ]

        for url in urls_liberadas:
            if request.path.startswith(url):
                return self.get_response(request)

        # 4. Verifica a Loja
        try:
            if hasattr(request.user, 'perfil') and request.user.perfil.loja:
                loja = request.user.perfil.loja
                
                # Rastreamento de uso
                loja.registrar_acesso()
                
                # Verifica se deve bloquear (Baseado na Data)
                esta_vencido = loja.verificar_bloqueio()
                
                if loja.status_assinatura == 'BLOQUEADO' or esta_vencido:
                    return redirect('assinatura_bloqueada')
                    
        except Exception as e:
            # Em produção, é melhor usar logging em vez de print
            print(f"Erro Middleware: {e}")

        return self.get_response(request)


class LoginProtecaoMiddleware:
    """Bloqueia tentativas de login quando IP está em cooldown (superusuário isento)."""

    ROTAS_LOGIN = ('/accounts/login/', '/api/login/')

    def __init__(self, get_response):
        self.get_response = get_response

    def _extrair_username(self, request):
        username = (request.POST.get('username') or '').strip()
        if username:
            return username
        if request.path == '/api/login/' and request.body:
            import json
            try:
                body = json.loads(request.body.decode('utf-8'))
                return (body.get('username') or '').strip()
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                pass
        return ''

    def __call__(self, request):
        if request.method == 'POST' and request.path in self.ROTAS_LOGIN:
            username = self._extrair_username(request)

            if not usuario_eh_superuser(username):
                ip = obter_ip_cliente(request)
                if ip_bloqueado(ip):
                    mins = minutos_restantes_bloqueio_ip(ip)
                    msg = (
                        f'Muitas tentativas de login. IP bloqueado por {mins} minuto(s). '
                        'Contate o administrador se precisar de acesso imediato.'
                    )
                    if request.path == '/api/login/':
                        return JsonResponse({'erro': msg, 'bloqueio_ip': True}, status=429)
                    messages.error(request, msg)
                    return redirect('login')

                if conta_congelada_username(username):
                    msg = (
                        'Conta congelada por segurança. '
                        'Solicite ao administrador do sistema para descongelar.'
                    )
                    if request.path == '/api/login/':
                        return JsonResponse({'erro': msg, 'conta_congelada': True}, status=403)
                    messages.error(request, msg)
                    return redirect('login')

        return self.get_response(request)


class SessaoUnicaMiddleware:
    """Encerra sessão web se login foi feito em outro navegador (superusuário isento)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            urls_liberadas = (
                reverse('logout'),
                '/admin/',
                '/static/',
                '/media/',
                '/accounts/login/',
            )
            if not any(request.path.startswith(u) for u in urls_liberadas):
                perfil = getattr(request.user, 'perfil', None)
                sk = request.session.session_key
                if perfil and perfil.session_key_ativa and sk and perfil.session_key_ativa != sk:
                    logout(request)
                    messages.warning(
                        request,
                        'Sessão encerrada: sua conta foi acessada em outro dispositivo.',
                    )
                    return redirect('login')

        return self.get_response(request)