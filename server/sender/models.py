#from typing import Iterable, Optional
from django.db import models
from django.utils.timezone import get_current_timezone
#from django.db.models import DateTimeField


#   Рассылка
class SendList(models.Model):
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
    t_zone = models.DateTimeField('часовой пояс')
#default=get_current_timezone()

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


