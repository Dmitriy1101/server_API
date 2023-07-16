from django.db.models import Prefetch, Count, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
#from rest_framework.permissions import IsAdminUser  #подключение авторизации только админ
from sender.models import Clients, SendList, Message
from sender.serializers import ClientsSerializer, MessageSerializer, SendListSerializer
from pytz import timezone
import time


#---------------------------------------------------
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
    filterset_fields = ['phone_number', 'phone_code', 'tags', 'time_zone']
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
    filterset_fields = ['date_start', 'send_text', 'filter', 'date_end']
    search_fields = ['filter', 'send_text']
    ordering_fields = ['id', 'date_start', 'date_end']
#    permission_classes = [IsAdminUser]  #подключение авторизации только админ


#---------------------------------------------------
class MessageViewSet(ReadOnlyModelViewSet):
    '''
        Модель Сообщения:
            - статистика
    '''
    queryset = Message.objects.all().prefetch_related(
        Prefetch('clients',
                 queryset=Clients.objects.all().only('phone_number', 'time_zone')),
        Prefetch('sendlist', 
                 queryset = SendList.objects.all().only('date_start', 'date_end')), 
        )
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['date_send', 'status_sent', 'clients', 'sendlist']
    search_fields = []
    ordering_fields = ['id', 'date_send', 'status_sent', 'clients', 'sendlist']
#    permission_classes = [IsAdminUser] #подключение авторизации только админ

#В конце добавим словарь с подсчетом количества сообщений
'''    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)
        
        response.data.append(queryset.aggregate(total = Count('id')))
        return response'''
#---------------------------------------------------
