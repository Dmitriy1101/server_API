from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import SendList, Clients, Message
from .tasks import create_messages
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

    def validate_date_end(self, value):
        if timezone.make_naive(value) <= datetime.datetime.now():
            raise ValidationError('Нельзя дату окончания создать в прошлом.')
        return value

    def create(self, validated_data):
        if validated_data['date_start'] >= validated_data['date_end']:
            raise ValidationError('Проблема с датами начала или конца. Дата начала не может быть после окончания.')
        instance = SendList.objects.create(**validated_data)
        validated_data['id'] = instance.id
        create_messages.delay(**validated_data)
        return instance

    def update(self, instance, validated_data):
        if instance.date_start <= datetime.now() or Message.objects.filter(date_send__gte = datetime.now(), sendlist__id = instance.id) != []:
            raise ValueError('Поздно менять сообщения')
        instance.date_start = validated_data.get('date_start', instance.date_start)
        instance.send_text = validated_data.get('send_text', instance.send_text)
        instance.filters = validated_data.get('filters', instance.filters)
        instance.date_end = validated_data.get('date_end', instance.date_end)
        validated_data['id'] = instance.id
        update_messages.delay(**validated_data)
        instance.save()
        return instance
#---------------------------------------------------

        
class MessageSerializer(serializers.ModelSerializer):
    '''
    сериализатор сообщений все по модели
    '''
    clients = serializers.CharField(source = 'clients.phone_number')
    sendlist = serializers.CharField(source = 'sendlist.send_text')

    class Meta:
        model = Message
        fields = ['id', 'date_send', 'status_sent', 'clients', 'sendlist']
        read_only_fields = []
#---------------------------------------------------        