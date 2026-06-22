from datetime import date

def saas_context(request):
    """
    Disponibiliza informações de assinatura (dias restantes) 
    para todos os templates globalmente.
    """
    contexto = {}
    
    if request.user.is_authenticated and hasattr(request.user, 'perfil') and request.user.perfil.loja:
        loja = request.user.perfil.loja
        
        if loja.data_vencimento:
            delta = loja.data_vencimento - date.today()
            dias_restantes = delta.days
            
            contexto['saas_dias_restantes'] = dias_restantes
            contexto['saas_vencido'] = (dias_restantes < 0)
            contexto['saas_alerta'] = (dias_restantes <= 5) 
            
    return contexto