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
        fields = ['id', 'phone_number', 'phone_code', 'tags', 'time_zone', 'birthdate']#, 't_zone']
        read_only_fields = []
          
    def create(self, validated_data): 
        birthdate = validated_data.pop('birthdate')
        time_zone = validated_data.pop('time_zone')
        if birthdate == None:
            birthdate="2000-01-01"
        if time_zone == None:
            time_zone="+0100"
        validated_data['t_zone'] = f'{birthdate}T00:00:00{time_zone}'
        return Clients.objects.create(**validated_data)
    
    def update (self, instance, validated_data):
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.phone_code = validated_data.get('phone_code', instance.phone_code)
        instance.tags = validated_data.get('tags', instance.tags)
        birthd = validated_data.pop('birthdate')
        timone = validated_data.pop('time_zone')
        if birthd== None:
            birthd="2000-01-01"
        if timone == None:
            timone="+0100"
        validated_data['t_zone'] = f'{birthd}T00:00:00{timone}'
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
    
    class Meta:
        model = Message
        fields = ['id', 'status_sent', 'clients', 'sendlist']
        read_only_fields = []
#---------------------------------------------------        