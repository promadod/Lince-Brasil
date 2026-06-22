from django.contrib import admin
from .models import Motorista, Corrida

@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'whatsapp') 
    search_fields = ('nome', 'whatsapp')      

@admin.register(Corrida)
class CorridaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nome', 'status', 'motorista')
    list_filter = ('status',)