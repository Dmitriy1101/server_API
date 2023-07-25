from celery import shared_task
from urllib3.util.retry import Retry
import requests, re 
from requests.adapters import HTTPAdapter
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Prefetch
from sender.models import Clients, SendList, Message


def take_it():
    with open('sender/my.txt', 'r', encoding='utf-8') as f:
        key = f.readline()
        return key

@shared_task
def activate_sending():
    sendlist_set = SendList.obgects.filter(date_start__lte = (datetime.now() + timedelta(days=1))).in_bulk()
    [MessageFather.validate_start_time(**sendlist) for sendlist in sendlist_set if sendlist_set != None]


class MessageFather:
    
    def __init__(self):
        self.url = 'https://probe.fbrq.cloud/v1/send/'
        self.token = take_it()
        
    @property
    def header(self):
         return {'Authorization': f'Bearer {self.token}'}

    @shared_task
    def validate_start_time(**sendlist_data):
        if timezone.make_naive(sendlist_data['date_start']) <= datetime.now():
#        if sendlist_data.date_start <= datetime.datetime.now:
            return MessageFather.create_and_send_messages.delay(sendlist_data)
        return

    def get_active_sendlist():
        pass

    @shared_task
    def take_this_messages():
        message_set = Message.objects.filter(date_send__lte = datetime.now()).prefetch_related(
            Prefetch('clients',
                 queryset=Clients.objects.all().only('phone_number', 'id')),
        )
        with requests.Session() as s:
            retry = Retry(connect = 3, backoff_factor = 0.5)
            adatper = HTTPAdapter(max_retries = retry)
            s.mount('http://', adapter = adatper)
            s.mount('https://', adapter = adatper)
            for message in message_set:
                url = f'http://localhost:8000/api/clients/{message.clients.id}/'
                data ={"phone_number": message.clients.phone_number, "phone": "111", "tags": 'victory', "time_zone": "-0000"}
                s.patch(url, headers = {"content-type": "application/json"}, data = data)
                print(s.text)
        return
    
    @shared_task
    def create_and_send_messages(sendlist_data):
        clients_set = Clients.objects.filter(tags__in = re.split(',', sendlist_data['filters']))
        if clients_set is None:
            return []
        message_set = Message.objects.bulk_create(
            [Message(date_send = datetime.now(), status_sent = "in_progres", clients = client, sendlist = SendList(**sendlist_data)) for client in clients_set]
            )
        return MessageFather.take_this_messages.delay()



