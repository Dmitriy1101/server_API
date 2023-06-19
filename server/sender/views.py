from django.db.models import Prefetch, Count, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
#from rest_framework.permissions import IsAdminUser  #подключение авторизации только админ
from sender.models import Clients, SendList, Message
from sender.serializers import ClientsSerializer, MessageSerializer, SendListSerializer



#---------------------------------------------------
'''
    Модель Клиент:
        - добавить
        - обновить
        - удалить
'''
#---------------------------------------------------
# Делаем через модель подробно
class ClientViewSet(ModelViewSet):
    queryset = Clients.objects.all()
    serializer_class = ClientsSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['phone_number', 'phone_code', 'tags', 't_zone']
    search_fields = ['tags']
    ordering_fields = ['id', 'phone_number', 'phone_code', 't_zone']
#    permission_classes = [IsAdminUser]   #подключение авторизации только админ
    



#---------------------------------------------------
'''
    Модель Рассылка:
        - добавить
        - общая статистика с группировкой по статусу
        - обновление
        - удаление
        - обработка активной
'''
#---------------------------------------------------
class SendListViewSet(ModelViewSet):
    queryset = SendList.objects.all()
    serializer_class = SendListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['date_start', 'send_text', 'filter', 'date_end']
    search_fields = ['filter', 'send_text']
    ordering_fields = ['id', 'date_start', 'date_end']
#    permission_classes = [IsAdminUser]  #подключение авторизации только админ



#---------------------------------------------------
'''
    Модель Сообщения:
        - статистика
'''
#---------------------------------------------------
class MessageViewSet(ReadOnlyModelViewSet):
    queryset = Message.objects.all().prefetch_related(
# В таком режие извлечения из бд для урезания запроса( .only('date_start', 'date_end', 'send_text') ) мы пишем новый 'вложеный' сериалезатор и
# не используя существующий, тк обычный приведет к увеличению числа запросов из за указанных полей(fields), или не используем вложеный сериализатор.
# ('date_start', 'date_end', 'send_text') должны совападать 
        Prefetch('clients',
                 queryset=Clients.objects.all().only('phone_number', 't_zone')),
        Prefetch('sendlist', 
                 queryset = SendList.objects.all().only('date_start', 'date_end')), 
        )#.annotate(some = F('clients__id') + F('sendlist__id')) # Добавляем поле some еще надо в serializers.py
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['date_send', 'status_sent', 'clients', 'sendlist']
    search_fields = []
    ordering_fields = ['id', 'date_send', 'status_sent', 'clients', 'sendlist']
#    permission_classes = [IsAdminUser] #подключение авторизации только админ

#В конце добавим словарь с подсчетом количества сообщений
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)
        
        response.data.append(queryset.aggregate(total = Count('id')))
        return response
#---------------------------------------------------
