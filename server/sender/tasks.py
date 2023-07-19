from celery import shared_task
import requests, json, re
from datetime import datetime
from sender.models import Clients, SendList, Message
from sender.serializers import ClientsSerializer


class MessageFather:
    
    def __init__(self, token, sendlist: SendList):
        self.token = token
        self.sendlist = sendlist
        self.clients = Clients.objects.filter(tags__icontains__in = re.split(',', sendlist.filters))
        
    @property
    def header(self):
         return {'Authorization': f'OAuth {self.token}'}
    
#    @shared_task
    def make_message_daddy(self, sendlist: SendList):
        clients_set = Clients.objects.filter(tags__icontains__in = re.split(',', sendlist.filters))
        if clients_set is None:
            return []
        message_set = []
        for client in clients_set:
            message = Message(clients = client, sendlist = sendlist)
            message_set.append(message)
            message.save()
        return message_set

    def take_this_messages(self, message_set):
        for message in message_set:
            client = [c for c in self.clients if c.id == message.clients_id]
            client = client[0]
            desp = requests.get('http://localhost:8000/api/clients/')
            print(desp.status_code)
            resp = requests.patch(f'http://localhost:8000/api/clients/{message.clients_id}/', data={"phone_number": "79876543210", "phone_code": "1", "tags": client.tags, "time_zone": "-0000"})
            print(resp.status_code)
        return

