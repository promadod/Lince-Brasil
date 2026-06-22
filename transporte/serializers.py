from rest_framework import serializers
from .models import Corrida,Motorista

class MotoristaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motorista
        fields = '__all__'

class CorridaSerializer(serializers.ModelSerializer):
    motorista_whatsapp = serializers.CharField(source='motorista.whatsapp', read_only=True)
    class Meta:
        model = Corrida
        fields = '__all__'
        read_only_fields = ['motorista', 'data_solicitacao']

    def create(self, validated_data):
        # Pega o usuário logado (ou define um padrão se for app aberto)
        # No caso do app cliente aberto, passaremos o ID do motorista via URL/JSON
        return super().create(validated_data)