from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import SendList, Clients, Message
import datetime

       
class ClientsSerializer(serializers.ModelSerializer):
    '''
    сериализатор клиентов
    все по модели + валидация номера телефрна и часового пояса
    '''
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
        if not (value.isdigit() and value.startswith('7')):
            raise ValidationError('Номер формата "7XXXXXXXX" где X цифра от 0 до 9')
        return value
#---------------------------------------------------   


class SendListSerializer(serializers.ModelSerializer):
    '''
    сериализатор рассылки выводим все по модели
    '''
    class Meta:
        model = SendList
        fields = ['id', 'date_start', 'send_text', 'filters', 'date_end']
        read_only_fields = []
#---------------------------------------------------

        
class MessageSerializer(serializers.ModelSerializer):
    '''
    сериализатор сообщений все по модели
    '''
    class Meta:
        model = Message
        fields = ['id', 'status_sent', 'clients', 'sendlist']
        read_only_fields = []
#---------------------------------------------------        