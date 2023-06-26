from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import SendList, Clients, Message
import time

       

#---------------------------------------------------
#Настроеное поле
class TimeCombineField(serializers.ModelField):
    '''
    2 fields in 1 tme
    '''
    
    def __init__(self, format_time: str, *args, **kwargs):
        self.format_time = format_time
        super().__init__(*args, **kwargs)
    
    #из базы 
    def to_representation(self, obj):
        value = self.model_field.value_from_object(obj)
        if type(value) == str:
            value = time.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
            return time.strftime(self.format_time, value)
        return value.strftime(self.format_time)
    
    #в базу возвращает строку времани в базу пойдет в методе create и  update
    def to_internal_value(self, data):
        return data
 
    
class ClientsSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(min_length = 11, required=True)

    time_zone = TimeCombineField(model_field=Clients._meta.get_field('t_zone'), format_time = '%z')
    birthdate = TimeCombineField(model_field=Clients._meta.get_field('t_zone'), format_time = '%Y-%m-%d')
    
    class Meta:
        model = Clients
        fields = ['id', 'phone_number', 'phone_code', 'tags', 'time_zone', 'birthdate']
        read_only_fields = []

    def make_str_field(self, birthdate = "2000-01-01", time_zone = "+0000"):
        return f'{birthdate}T00:00:00{time_zone}'
          
    def create(self, validated_data):
        validated_data['t_zone'] = self.make_str_field(
            birthdate = validated_data.pop('birthdate'),
            time_zone = validated_data.pop('time_zone'),   
            )
        return Clients.objects.create(**validated_data)
    
    def update (self, instance, validated_data):
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.phone_code = validated_data.get('phone_code', instance.phone_code)
        instance.tags = validated_data.get('tags', instance.tags)
        validated_data['t_zone'] = self.make_str_field(
            birthdate = validated_data.pop('birthdate'),
            time_zone = validated_data.pop('time_zone'),   
            )
        instance.t_zone = validated_data.get('t_zone', instance.t_zone)
        instance.save()
        return instance


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

# Возможна реализация через ".annotate(some = ..." во views.py. Добавляем поле some.
    some = serializers.SerializerMethodField()    
    def get_some(self, instance):
        date = instance.clients.t_zone
        return date.strftime('%Y%b%d%z')
   
    
    class Meta:
        model = Message
        fields = ['id', 'status_sent', 'clients', 'sendlist', 'some'] # Добавляем поле some 
        read_only_fields = []
#---------------------------------------------------        