from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import SendList, Clients, Message


       


class ClientsSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(min_length = 11, required=True)
    
    class Meta:
        model = Clients
        fields = ['id', 'phone_number', 'phone_code', 'tags', 't_zone']
        read_only_fields = []
        
    def validate_phone_number(self, value):
        if not (value.isdigit() and value[0] == "7"):
            raise ValidationError('Номер формата "7XXXXXXXX" где X цифра от 0 до 9')
        return value



class SendListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendList
        fields = ['id', 'date_start', 'send_text', 'filter', 'date_end']
        read_only_fields = []
        
# вложеный серриализатор рассылки      
class IncSendListSerializer(SendListSerializer):
    class Meta:
        model = SendList
        fields = ['date_start', 'date_end']



class MessageSerializer(serializers.ModelSerializer):
#    без вложеного сериализатора
    clients = serializers.CharField(source = 'clients.phone_number')
#    sendlist = serializers.CharField(source = 'sendlist.send_text')
    sendlist = IncSendListSerializer()

# Добавляем поле some, надо еще во views.py
#    some = serializers.SerializerMethodField()    
#    def get_some(self, instance):
#        return instance.some
   
    
    class Meta:
        model = Message
        fields = ['id', 'status_sent', 'clients', 'sendlist']#, 'some'] # Добавляем поле some 
        read_only_fields = []
        