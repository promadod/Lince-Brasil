from django.shortcuts import redirect
from django.urls import reverse
from .models import Loja

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