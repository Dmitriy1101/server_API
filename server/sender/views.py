#from django.db.models import Prefetch, Count, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
#from rest_framework.permissions import IsAdminUser  #подключение авторизации только админ
from sender.models import Clients, SendList, Message
from sender.serializers import ClientsSerializer, MessageSerializer, SendListSerializer


# Делаем через модель подробно
class ClientViewSet(ModelViewSet):
    '''
        Модель Клиент:
            - добавить
            - обновить
            - удалить
    '''
    queryset = Clients.objects.all()
    serializer_class = ClientsSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'phone_number', 'phone_code', 'tags', 'time_zone']
    search_fields = ['tags']
    ordering_fields = ['id', 'phone_number', 'phone_code', 'time_zone']
#    permission_classes = [IsAdminUser]   #подключение авторизации только админ
#---------------------------------------------------


class SendListViewSet(ModelViewSet):
    '''
        Модель Рассылка:
            - добавить
            - общая статистика с группировкой по статусу
            - обновление
            - удаление
            - обработка активной
    '''
    queryset = SendList.objects.all()
    serializer_class = SendListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'date_start', 'send_text', 'filters', 'date_end']
    search_fields = ['filters', 'send_text']
    ordering_fields = ['id', 'date_start', 'date_end']
#    permission_classes = [IsAdminUser]  #подключение авторизации только админ
#---------------------------------------------------


class MessageViewSet(ReadOnlyModelViewSet):
    '''
        Модель Сообщения:
            - статистика
    '''
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id', 'date_send', 'status_sent', 'clients', 'sendlist']
    search_fields = []
    ordering_fields = ['id', 'date_send', 'status_sent', 'clients', 'sendlist']
#    permission_classes = [IsAdminUser] #подключение авторизации только админ
#---------------------------------------------------
