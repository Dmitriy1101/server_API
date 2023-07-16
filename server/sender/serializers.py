from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import SendList, Clients, Message
import datetime

       
#---------------------------------------------------   
class ClientsSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(min_length = 11, required=True)
    
    class Meta:
        model = Clients
        fields = ['id', 'phone_number', 'phone_code', 'tags', 'time_zone']
        read_only_fields = []

    def validate_time_zone(self, value):
        if isinstance(datetime.datetime.strptime(value, '%z').tzinfo, datetime.timezone):
            return value
        raise serializers.ValidationError('Неверный часовой пояс. Часовой пояс ожидается в формате +HH:MM или -HH:MM')

    def validate_phone_number(self, value):
        if value.startswith('7'):
            return value
        raise serializers.ValidationError('7XXXXXXXXXX формат ввода')


#---------------------------------------------------
class SendListSerializer(serializers.ModelSerializer):

    class Meta:
        model = SendList
        fields = ['id', 'date_start', 'send_text', 'filter', 'date_end']
        read_only_fields = []
#---------------------------------------------------

        
# вложеный серриализатор рассылки      
class IncSendListSerializer(SendListSerializer):

    class Meta:
        model = SendList
        fields = ['date_start', 'date_end']


#---------------------------------------------------
class MessageSerializer(serializers.ModelSerializer):
#    без вложеного сериализатора
    clients = serializers.CharField(source = 'clients.phone_number') #клиент выводим не id а номер телефона 
#    sendlist = serializers.CharField(source = 'sendlist.send_text') #рассылка выводим не id а текст
    sendlist = IncSendListSerializer() #рассылка выводим не id а вложеный серриализатор
    
    class Meta:
        model = Message
        fields = ['id', 'status_sent', 'clients', 'sendlist']
        read_only_fields = []
#---------------------------------------------------        