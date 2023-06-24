from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import SendList, Clients, Message


       


class ClientsSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(min_length = 11, required=True)
    
    class Meta:
        model = Clients
        fields = ['id', 'phone_number', 'phone_code', 'tags', 't_zone', 'main_date']
        read_only_fields = []
        
    def validate_phone_number(self, value):
        if not (value.isdigit() and value[0] == "7"):
            raise ValidationError('Номер формата "7XXXXXXXX" где X цифра от 0 до 9')
        return value

    main_date = serializers.SerializerMethodField() 
    def get_main_date(self, instance):
        return instance.main_date



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
    clients = serializers.CharField(source = 'clients.phone_number') #клиент выводим не id а номер телефона 
#    sendlist = serializers.CharField(source = 'sendlist.send_text') #рассылка выводим не id а текст
    sendlist = IncSendListSerializer() #рассылка выводим не id а вложеный серриализатор

# Добавляем поле some, надо еще во views.py
#    some = serializers.SerializerMethodField()    
#    def get_some(self, instance):
#        return instance.some
   
    
    class Meta:
        model = Message
        fields = ['id', 'status_sent', 'clients', 'sendlist']#, 'some'] # Добавляем поле some 
        read_only_fields = []
        