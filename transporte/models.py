from django.db import models
from django.conf import settings

# --- TABELA: PERFIL DO MOTORISTA ---
class Motorista(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil_motorista')
    nome = models.CharField(max_length=100)
    whatsapp = models.CharField(max_length=20, null=True, blank=True)
    chave_pix = models.CharField(max_length=100, null=True, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

# --- TABELA DE CORRIDAS ATUALIZADA ---
class Corrida(models.Model):
    STATUS_CHOICES = [
        ('SOLICITADO', 'Solicitado'),
        ('ACEITO', 'Aceito'),
        ('EM_ROTA', 'Motorista a Caminho'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]

    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE, related_name='corridas', null=True, blank=True)
    venda_pdv_id = models.IntegerField(null=True, blank=True) # <-- O elo de ligação
    
    cliente_nome = models.CharField(max_length=100)
    cliente_whatsapp = models.CharField(max_length=20, blank=True, null=True)
    origem_texto = models.CharField(max_length=255)
    destino_texto = models.CharField(max_length=255)
    origem_lat = models.CharField(max_length=50, blank=True, null=True)
    origem_long = models.CharField(max_length=50, blank=True, null=True)
    destino_lat = models.CharField(max_length=50, blank=True, null=True)
    destino_long = models.CharField(max_length=50, blank=True, null=True)
    distancia_km = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    tempo_estimado_minutos = models.IntegerField(default=0)
    valor_cobrado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SOLICITADO')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_agendamento = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"{self.cliente_nome} - {self.status}"

    # ==========================================================
    # A MÁGICA DA SINCRONIZAÇÃO REVERSA (CORRIGIDA)
    # ==========================================================
    def save(self, *args, **kwargs):
        # 1. Salva a corrida normalmente no banco do MoveON
        super().save(*args, **kwargs)
        
        # 2. Se for uma corrida que veio do PDV, sincroniza o status de volta!
        if self.venda_pdv_id:
            try:
                from app_pdv.models import Venda # Importação local para evitar conflito
                venda = Venda.objects.get(id=self.venda_pdv_id)
                
                # Quando o app MoveON manda o sinal de "Aceito":
                if self.status == 'ACEITO' or self.status == 'EM_ANDAMENTO':
                    venda.status_entrega = 'EM_ROTA'
                    venda.status = 'SAIU_ENTREGA' # <--- É ESSA LINHA QUE MOVE O CARD NA TORRE!
                    venda.save()
                    
                # Quando o app MoveON manda o sinal de "Finalizado":
                elif self.status == 'CONCLUIDO':
                    venda.status_entrega = 'ENTREGUE'
                    venda.status = 'FINALIZADO'   # <--- É ESSA LINHA QUE TIRA O CARD DA TORRE!
                    venda.save()
                    
                # Se o motorista rejeitar ou cancelar a corrida:
                elif self.status == 'CANCELADO':
                    venda.status_entrega = 'PENDENTE'
                    venda.status = 'EM_PREPARACAO' # <--- Devolve o card pra coluna do meio
                    venda.save()
                    
            except Exception as e:
                print(f"Erro na sincronização reversa: {e}")