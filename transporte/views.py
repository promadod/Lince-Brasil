from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Corrida, Motorista
from .serializers import CorridaSerializer, MotoristaSerializer

PRECO_GLOBAL = 2.0 # Valor padrão de corridas inicial, podendo alterar no app do motorista
ACEITA_IMEDIATAS = True # Funcao para aceitar ambos tipos de corridas ou apenas agendamento
TAXA_DESLOCAMENTO = 0.0 # taxa de deslocamento fixa do motorista
LIMITE_10KM = False

AGENDA_GLOBAL = {
    'Segunda-feira': {'aberto': True, 'inicio': '08:00', 'fim': '18:00'},
    'Terça-feira': {'aberto': True, 'inicio': '08:00', 'fim': '18:00'},
    'Quarta-feira': {'aberto': True, 'inicio': '08:00', 'fim': '18:00'},
    'Quinta-feira': {'aberto': True, 'inicio': '08:00', 'fim': '18:00'},
    'Sexta-feira': {'aberto': True, 'inicio': '08:00', 'fim': '18:00'},
    'Sábado': {'aberto': True, 'inicio': '08:00', 'fim': '12:00'},
    'Domingo': {'aberto': False, 'inicio': '08:00', 'fim': '12:00'}
}

class CorridaViewSet(viewsets.ModelViewSet):
    queryset = Corrida.objects.all()
    serializer_class = CorridaSerializer
    
    # --- MUDANÇA 1: Libera acesso sem login por enquanto ---
    permission_classes = [permissions.AllowAny] 

    def get_queryset(self):
        queryset = Corrida.objects.all().order_by('-data_solicitacao')
        
        # Filtro para o Motorista (Status)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # NOVO: Filtro para o Cliente (Pelo WhatsApp)
        whatsapp = self.request.query_params.get('cliente_whatsapp')
        if whatsapp:
            queryset = queryset.filter(cliente_whatsapp=whatsapp)
            
        return queryset

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def solicitar(self, request):
        # ... (seu código de solicitar continua igual)
        data = request.data
        motorista_id = data.get('motorista_id')
        serializer = CorridaSerializer(data=data)
        if serializer.is_valid():
            serializer.save(motorista_id=motorista_id, status='SOLICITADO')
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.AllowAny])
    def atualizar_status(self, request, pk=None):
        # ... (seu código de atualizar status continua igual)
        corrida = self.get_object()
        novo_status = request.data.get('status')
        if novo_status in ['ACEITO', 'EM_ANDAMENTO', 'CONCLUIDO', 'CANCELADO']:
            corrida.status = novo_status
            corrida.save()
            return Response({'status': 'atualizado'})
        return Response({'erro': 'Status inválido'}, status=400)
    
    @action(detail=False, methods=['get', 'post'], permission_classes=[permissions.AllowAny])
    def gerenciar_preco(self, request):
        global PRECO_GLOBAL, TAXA_DESLOCAMENTO
        if request.method == 'POST':
            # Motorista definindo novo preço
            novo_valor = request.data.get('valor')
            nova_taxa = request.data.get('taxa')
            if novo_valor:
                PRECO_GLOBAL = float(novo_valor)
            if nova_taxa is not None:
                TAXA_DESLOCAMENTO = float(nova_taxa)
            return Response({'valor': PRECO_GLOBAL, 'taxa': TAXA_DESLOCAMENTO})
        else:
            # Cliente ou Motorista consultando preço
            return Response({'valor': PRECO_GLOBAL, 'taxa': TAXA_DESLOCAMENTO})
    
    @action(detail=False, methods=['get', 'post'], permission_classes=[permissions.AllowAny])
    def status_imediato(self, request):
        global ACEITA_IMEDIATAS
        if request.method == 'POST':
            # Motorista ativando/desativando
            novo_status = request.data.get('ativo')
            if novo_status is not None:
                ACEITA_IMEDIATAS = bool(novo_status)
            return Response({'ativo': ACEITA_IMEDIATAS})
        else:
            # Cliente consultando
            return Response({'ativo': ACEITA_IMEDIATAS})
        
    @action(detail=False, methods=['get', 'post'], permission_classes=[permissions.AllowAny])
    def limite_km(self, request):
        global LIMITE_10KM
        if request.method == 'POST':
            novo_status = request.data.get('ativo')
            if novo_status is not None:
                LIMITE_10KM = bool(novo_status)
            return Response({'ativo': LIMITE_10KM})
        else:
            return Response({'ativo': LIMITE_10KM})
        
    @action(detail=False, methods=['get', 'post'], permission_classes=[permissions.AllowAny])
    def gerenciar_agenda(self, request):
        global AGENDA_GLOBAL
        if request.method == 'POST':
            AGENDA_GLOBAL = request.data
            return Response(AGENDA_GLOBAL)
        return Response(AGENDA_GLOBAL)
        
class MotoristaViewSet(viewsets.ModelViewSet):
    queryset = Motorista.objects.all()
    serializer_class = MotoristaSerializer
    permission_classes = [AllowAny]