from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Importa as views do seu arquivo transporte/views.py
from .views import Corrida, Motorista # Se houver ViewSets, importe eles aqui (ex: CorridaViewSet)

# Como não tenho certeza do nome exato da classe no seu transporte/views.py, 
# se você usou ViewSets do Django Rest Framework (DRF), o código é este:
from .views import CorridaViewSet, MotoristaViewSet

router = DefaultRouter()
router.register(r'corridas', CorridaViewSet, basename='corrida')
router.register(r'motoristas', MotoristaViewSet, basename='motorista')

urlpatterns = [
    path('', include(router.urls)),
]