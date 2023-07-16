#from typing import Iterable, Optional
import datetime
from django.db import models
from django.utils.timezone import get_current_timezone, make_aware



class MyDateTimeField(models.DateTimeField):\
'''    
        def to_python(self, value):
            if isinstance(value, datetime.datetime):
#                val_tz = value.tzinfo
#                value = datetime.datetime(value.year, value.month, value.day, tzinfo = value.tzinfo)
#                value = self.make_aware(value, value.tzinfo)
                return  value
            elif isinstance(value, str):
#                value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
                return  datetime.datetime.fromisoformat(value)
            else: 
                return super().to_python(self)
'''

class SendList(models.Model):
    '''
        Модель рассылки:
            - дата начала
            - дата конца
            - фильтр
            - текст
    '''
    date_start = models.DateTimeField('Начало рассылки',auto_now_add=False)
    send_text = models.TextField('Текст', max_length=255)
    filter = models.TextField('Фильтры', max_length=127)
    date_end = models.DateTimeField('Конец рассылки',auto_now_add=False)

    
    def __str__(self):
        return str(self.send_text)
    
    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        
        

#   Клиенты          
class Clients(models.Model):
    phone_number = models.CharField('Телефон',unique=True , max_length=11)
    phone_code = models.CharField('Код оператора', max_length=10)
    tags = models.CharField('Тэги', max_length=127)
    time_with_zone = MyDateTimeField('часовой пояс')

    def __str__(self):
        return str(self.phone_number)
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'



#  Сообщения
class Message(models.Model):
    date_send = models.DateTimeField('Начало рассылки',auto_now_add=True)
    status_sent = models.BooleanField('Доставлено', blank=True)
    clients = models.ForeignKey(Clients, on_delete=models.PROTECT, null=True, related_name='message')
    sendlist = models.ForeignKey(SendList, on_delete=models.PROTECT, null=True, related_name='message')

    
    def __str__(self):
        return str(self.status_sent)
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


