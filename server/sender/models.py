from django.db import models


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
    filters = models.TextField('Фильтры', max_length=127)
    date_end = models.DateTimeField('Конец рассылки',auto_now_add=False)

    
    def __str__(self):
        return str(self.send_text)

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        
                
class Clients(models.Model):
    '''
        Модель клиенты:
            - номер телефона клиента в формате 7XXXXXXXXXX (X - цифра от 0 до 9)
            - код мобильного оператора
            - тег (произвольная метка)
            - часовой пояс
    '''
    phone_number = models.CharField('Телефон',unique=True , max_length=11)
    phone_code = models.CharField('Код оператора', max_length=10)
    tags = models.CharField('Тэги', max_length=127)
    time_zone = models.CharField('часовой пояс', max_length=20)

    def __str__(self):
        return str(self.phone_number)
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    '''
        Модель сообщения:
            - дата и время создания (отправки)
            - статус отправки
            - id рассылки, в рамках которой было отправлено сообщение
            - id клиента, которому отправили
    '''
    
    date_send = models.DateTimeField('Начало рассылки', null=False)
    status_sent = models.CharField('Статус', default="written")
    clients = models.ForeignKey(Clients, on_delete=models.PROTECT, null=True, related_name='message')
    sendlist = models.ForeignKey(SendList, on_delete=models.PROTECT, null=True, related_name='message')

    
    def __str__(self):
        return str(self.status_sent)
        
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


