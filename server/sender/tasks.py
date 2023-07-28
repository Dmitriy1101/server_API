from celery import shared_task
from urllib3.util.retry import Retry
import requests, re , pytz
from datetime import datetime, timedelta as dt
from requests.adapters import HTTPAdapter
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Prefetch
from sender.models import Clients, SendList, Message


@shared_task
def messagefather_keeper():
    '''Каждый час проверяет сообщенияя готовые к отправке в течении часа, создает задачу на рассылку по времени.'''

    send_set = Message.obgects.filter(sendlist__date_end__gte = datetime.now()).filter(date_send__lte = datetime.now()).filter(status_sent = "written")
    if send_set:
        time_list = []
        (time_list.append(message.date_send) for message in send_set if message.date_send not in time_list)
        for t in time_list:
            MessageFather().send_messages.apply_async(sendlist, eta = timezone.make_naive(sendlist.date_start))

@shared_task
def create_messages(**sendlist_data):
    '''Создает сообщения и инициирует немедленную рассылку(покачто так)'''

    clients_set = Clients.objects.filter(tags__in = re.split(',', sendlist_data['filters']))
    if clients_set is None:
        return []
    message_set = Message.objects.bulk_create(
        [Message(
            date_send = timezone.make_naive(sendlist_data['date_start'], datetime.strptime(client.time_zone, '%z').tzinfo), 
            status_sent = "written", 
            clients = client, 
            sendlist = SendList(**sendlist_data)
            ) for client in clients_set]
        )
    if timezone.make_naive(sendlist_data['date_start']) <= datetime.now():
        f = MessageFather()
        cache.set(f.cache_key, message_set, 60*10)
        f.send_messages.delay()
    return 

class MessageFather:
    '''
    Рассылка сообщений 
    '''
    
    def __init__(self, cache_key = None, retry = False):
        if cache_key == None:
            self.cache_key = f'Cache object:{id(self)}'
        else:
            self.cache_key = cache_key
        self.resp_dict = {}

    @property
    def status(self):    
        '''На случай повторной рассылки'''

        if retry:
            return "in_progres"
        else:
            return "written"
        
    @property
    def url(self):
         return 'https://probe.fbrq.cloud/v1/send/'

    @property
    def token(self):
        '''(покачто так)'''
        with open('sender/my.txt', 'r', encoding='utf-8') as f:
            return f.readline()

    @property    
    def messages(self):
        '''Возвращаем список сообщений, если списка нету в кэше, то создаем и помещаем в кэш'''
        message_set = cache.get(self.cache_key)
        if message_set:
            return message_set
        else:
            message_set = Message.objects.filter(sendlist__date_end__gte = datetime.now()).filter(date_send__lte = datetime.now()).filter(status_sent = self.status).prefetch_related(
                Prefetch('clients',queryset=Clients.objects.all().only('phone_number', 'id')),
                Prefetch('sendlist',queryset=Clients.objects.all().only('send_text', 'date_end')),
            )
            cache.set(self.cache_key, message_set, 60*10)
            return message_set

    @shared_task
    def send_messages():
        '''Отправляет сообщения получателю(покачто так)'''
        message_set = self.messages
        with requests.Session() as s:
            retry = Retry(connect = 3, backoff_factor = 0.5)
            adatper = HTTPAdapter(max_retries = retry)
            s.headers.update({"Authorization": f"Bearer {self.token}"})
#            s.mount('http://', adapter = adatper)
            s.mount(url, adapter = adatper)
#            s.hooks['responce'].append(session_hook)
            for message in message_set:
                data ={"id": message.id, "phone": message.clients.phone_number, "text": message.sendlist.send_text}
                s.post(f'{self.url}{message.id}', data = data)
                self.resp_dict[message.id] = s.status_code
        return self.try_to_end.delay()

    @shared_task
    def try_to_end(self):
        '''Проверяем результат'''
        message_set = self.messages
        for message in message_set:
            if self.resp_dict[message.id] == 200:
                message_set.message.status_sent = "Compleate"
            elif timezone.make_naive(self.end) >= datetime.now():
                message_set.message.status_sent = "in_progres"
            else:
                message_set.message.status_sent = f"resp status: {self.resp_dict[message.id]}"
        message_set.update()
        message_set = message_set.filter(status_sent = "in_progres")
        if message_set != []:
            cache.set(self.cache_key, message_set, 60*10)
            self.retry = True
            return self.send_messages.apply_async(countdown = 60*5)
        return
