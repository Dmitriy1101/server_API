from celery import shared_task
from urllib3.util.retry import Retry
import requests, re 
from requests.adapters import HTTPAdapter
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db.models import Prefetch
from sender.models import Clients, SendList, Message


@property
def keper_key():
    return  'messagef_keeper'

@shared_task
def messagefather_keeper():
    sendlist_set = SendList.obgects.filter(date_start__lte = (datetime.now() + timedelta(days=1)))
    if sendlist_set:
        cache.set(keper_key, sendlist_set, 60)
        for sendlist in sendlist_set:
            MessageFather().validate_start_time.apply_async(sendlist, eta = sendlist.date_start)


@shared_task
def create_messages(self, **sendlist_data):
    clients_set = Clients.objects.filter(tags__in = re.split(',', sendlist_data['filters']))
    if clients_set is None:
        return []
    message_set = Message.objects.bulk_create(
        [Message(date_send = timezone.make_naive(sendlist_data['date_start'].), status_sent = "written", clients = client, sendlist = SendList(**sendlist_data)) for client in clients_set]
        )
    cache.set(self.cache_key, message_set, 60)
    return self.send_messages.delay()

class MessageFather:
    '''
    Рассылка и создание сообщений 
    '''
    
    def __init__(self):
        self.cache_key = f'Cache object:{id(self)}'
        self.resp_dict = {}
        
    @property
    def url(self):
         return 'https://probe.fbrq.cloud/v1/send/'

    @property
    def token(self):
        with open('sender/my.txt', 'r', encoding='utf-8') as f:
            return f.readline()

    @property    
    def messages(self):
        message_set = cache.get(self.cache_key)
        if message_set:
            return message_set
        else:
            message_set = Message.objects.filter(sendlist = self.list_id).filter(status_sent = "in_progres").prefetch_related(
                Prefetch('clients',queryset=Clients.objects.all().only('phone_number', 'id')),
                Prefetch('sendlist',queryset=Clients.objects.all().only('send_text', 'date_end')),
            )
            cache.set(self.cache_key, message_set, 60)
            return message_set

    @shared_task
    def validate_start_time(self, **sendlist_data):
        if timezone.make_naive(sendlist_data['date_start']) <= datetime.now():
            self.list_id = sendlist_data['id']
            self.end = sendlist_data['date_end']
            return self.create_messages.delay(sendlist_data)
        return

    @shared_task
    def create_messages(self, **sendlist_data):
        clients_set = Clients.objects.filter(tags__in = re.split(',', sendlist_data['filters']))
        if clients_set is None:
            return []
        message_set = Message.objects.bulk_create(
            [Message(date_send = datetime.now(), status_sent = "in_progres", clients = client, sendlist = SendList(**sendlist_data)) for client in clients_set]
            )
        cache.set(self.cache_key, message_set, 60)
        return self.send_messages.delay()

    @shared_task
    def send_messages():
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
    def try_to_end():
        message_set = self.messages
        for message in message_set:
            if self.resp_dict[message.id] == 200:
                message_set.message.status_sent = "Compleate"
            elif timezone.make_naive(self.end) >= datetime.now():
                pass
            else:
                message_set.message.status_sent = f"resp status: {self.resp_dict[message.id]}"
        Message.objects.bulk_create(
            [message and message_setdel(message) for message in message_set if message.status_sent != "in_progres"]
            )
        if message_set != []:
            cache.set(self.cache_key, message_set, 60*6)
            return self.send_messages.apply_async(countdown = 60*5)
        return

