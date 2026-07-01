from rest_framework import viewsets, permissions

from rest_framework.decorators import action

from rest_framework.response import Response

from rest_framework.permissions import AllowAny

from .models import Corrida, Motorista

from .serializers import CorridaSerializer, MotoristaSerializer



PRECO_GLOBAL = 2.0

ACEITA_IMEDIATAS = True

TAXA_DESLOCAMENTO = 0.0

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





def _reparar_corridas_pdv_presas():

    """Corridas PDV em CANCELADO com venda ainda pendente voltam para SOLICITADO."""

    from app_pdv.models import Venda

    vendas_pendentes = Venda.objects.filter(

        eh_entrega=True,

        status_entrega='PENDENTE',

    ).values_list('id', flat=True)

    if not vendas_pendentes:

        return

    Corrida.objects.filter(

        venda_pdv_id__in=list(vendas_pendentes),

        status='CANCELADO',

    ).update(motorista=None, status='SOLICITADO')





def _devolver_corrida_pdv_fila(corrida):

    """Devolve entrega PDV para a fila (disponível para qualquer motorista)."""

    from app_pdv.models import Venda

    if corrida.venda_pdv_id:

        Venda.objects.filter(id=corrida.venda_pdv_id).update(

            status_entrega='PENDENTE',

            status='EM_PREPARACAO',

            entregador_id=None,

        )

    Corrida.objects.filter(pk=corrida.pk).update(

        motorista_id=None,

        status='SOLICITADO',

    )

    corrida.refresh_from_db()





class CorridaViewSet(viewsets.ModelViewSet):

    queryset = Corrida.objects.all()

    serializer_class = CorridaSerializer

    permission_classes = [permissions.AllowAny]



    def get_queryset(self):

        _reparar_corridas_pdv_presas()



        queryset = Corrida.objects.all().order_by('-data_solicitacao')



        status = self.request.query_params.get('status')

        if status:

            queryset = queryset.filter(status=status)



        whatsapp = self.request.query_params.get('cliente_whatsapp')

        if whatsapp:

            queryset = queryset.filter(cliente_whatsapp=whatsapp)



        return queryset



    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])

    def solicitar(self, request):

        data = request.data

        motorista_id = data.get('motorista_id')

        serializer = CorridaSerializer(data=data)

        if serializer.is_valid():

            serializer.save(motorista_id=motorista_id, status='SOLICITADO')

            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)



    @action(detail=True, methods=['patch'], permission_classes=[permissions.AllowAny])

    def atualizar_status(self, request, pk=None):

        corrida = self.get_object()

        novo_status = request.data.get('status')

        if novo_status not in ['ACEITO', 'EM_ANDAMENTO', 'CONCLUIDO', 'CANCELADO']:

            return Response({'erro': 'Status inválido'}, status=400)



        if novo_status == 'CANCELADO' and corrida.venda_pdv_id:

            _devolver_corrida_pdv_fila(corrida)

            return Response({'status': 'devolvido_fila', 'corrida_id': corrida.id})



        corrida.status = novo_status

        corrida.save()

        return Response({'status': 'atualizado'})



    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])

    def devolver_fila(self, request, pk=None):

        corrida = self.get_object()

        if not corrida.venda_pdv_id:

            return Response({'erro': 'Corrida não é de loja PDV.'}, status=400)

        if corrida.status == 'CONCLUIDO':

            return Response({'erro': 'Entrega já finalizada.'}, status=400)

        _devolver_corrida_pdv_fila(corrida)

        return Response({'status': 'devolvido_fila', 'corrida_id': corrida.id})



    @action(detail=False, methods=['get', 'post'], permission_classes=[permissions.AllowAny])

    def gerenciar_preco(self, request):

        global PRECO_GLOBAL, TAXA_DESLOCAMENTO

        if request.method == 'POST':

            novo_valor = request.data.get('valor')

            nova_taxa = request.data.get('taxa')

            if novo_valor:

                PRECO_GLOBAL = float(novo_valor)

            if nova_taxa is not None:

                TAXA_DESLOCAMENTO = float(nova_taxa)

            return Response({'valor': PRECO_GLOBAL, 'taxa': TAXA_DESLOCAMENTO})

        return Response({'valor': PRECO_GLOBAL, 'taxa': TAXA_DESLOCAMENTO})



    @action(detail=False, methods=['get', 'post'], permission_classes=[permissions.AllowAny])

    def status_imediato(self, request):

        global ACEITA_IMEDIATAS

        if request.method == 'POST':

            novo_status = request.data.get('ativo')

            if novo_status is not None:

                ACEITA_IMEDIATAS = bool(novo_status)

            return Response({'ativo': ACEITA_IMEDIATAS})

        return Response({'ativo': ACEITA_IMEDIATAS})



    @action(detail=False, methods=['get', 'post'], permission_classes=[permissions.AllowAny])

    def limite_km(self, request):

        global LIMITE_10KM

        if request.method == 'POST':

            novo_status = request.data.get('ativo')

            if novo_status is not None:

                LIMITE_10KM = bool(novo_status)

            return Response({'ativo': LIMITE_10KM})

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


