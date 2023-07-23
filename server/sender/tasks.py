from celery import shared_task
#from celery_app import app
import requests, re
from django.utils import timezone
from datetime import datetime
from django.db.models import Prefetch
from sender.models import Clients, SendList, Message


@shared_task
def activate_sending():
    pass

class MessageFather:
    
    def __init__(self, token = 'G'):
        self.token = token
        
    @property
    def header(self):
         return {'Authorization': f'OAuth {self.token}'}
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
        for message in message_set:
            resp = requests.patch(f'http://localhost:8000/api/clients/{message.clients.id}/', data={"phone_number": message.clients.phone_number, "phone_code": "111", "tags": 'victory', "time_zone": "-0000"})
        return resp.status_code
    
    @shared_task
    def create_and_send_messages(sendlist_data):
        clients_set = Clients.objects.filter(tags__in = re.split(',', sendlist_data['filters']))
        if clients_set is None:
            return []
        message_set = Message.objects.bulk_create(
            [Message(date_send = datetime.now(), status_sent = "in_progres", clients = client, sendlist = SendList(**sendlist_data)) for client in clients_set]
            )
        return MessageFather.take_this_messages.delay()



