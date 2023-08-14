from celery import shared_task
from urllib3.util.retry import Retry
import requests, re , pytz, numpy, logging
from datetime import datetime, timedelta as dt
from requests.adapters import HTTPAdapter
from django.utils import timezone
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Prefetch
from sender.models import Clients, SendList, Message


def get_cache_key(somefing):
        k = '{:.9}'.format(str(id(somefing)))
        return f'Object{k}'

@shared_task(name = 'timer')
def message_keeper():
    '''Каждый час проверяет сообщенияя готовые к отправке в течении часа, создает задачу на рассылку по времени.'''

    send_set = Message.objects.filter(sendlist__date_end__gte =datetime.now()).filter(date_send__lte = datetime.now()).filter(status_sent = "written").prefetch_related(
        Prefetch('clients',queryset=Clients.objects.all().only('phone_number', 'time_zone')),
        Prefetch('sendlist',queryset=SendList.objects.all().only('send_text', 'date_end')),
        )
    if send_set:
        key = get_cache_key(send_set)
        cache.set(key, send_set, 60*5)
        send_messages.delay(cache_key = key)

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
        
        key = get_cache_key(message_set)
        cache.set(key, message_set, 60*10)
        return send_messages.delay(cache_key = key)
    return

@shared_task
def update_messages(**sendlist_data):
    '''Пересоздадим сообщения'''
    send_set = Message.objects.filter(sendlist__id = sendlist_data['id']).adelete()
    create_messages.delay(**sendlist_data)
          

def get_url():
    return 'http://My_URL'

def get_token():
    return {"Authorization": f"Bearer JWT token"}
  
def get_messages(cache_key):
    '''Возвращаем список сообщений, если списка нету в кэше, то создаем и помещаем в кэш'''
    message_set = cache.get(cache_key)
    if message_set:
        return message_set
    else:
        message_set = Message.objects.filter(sendlist__date_end__gte = datetime.now()).filter(date_send__lte = datetime.now(), status_sent = "written").prefetch_related(
            Prefetch('clients',queryset=Clients.objects.all().only('phone_number', 'time_zone')),
            Prefetch('sendlist',queryset=SendList.objects.all().only('send_text', 'date_end')),
        )
        cache.set(cache_key, message_set, 60*10)
        return message_set

@shared_task
def send_messages(cache_key = None):
    '''Отправляет сообщения получателю(покачто так)'''
    if not cache_key:
        cache_key = get_cache_key('ping-pong')
    resp_dict = {}
    message_set = get_messages(cache_key)
    with requests.Session() as s:
        retry = Retry(connect = 3, backoff_factor = 0.5)
        adatper = HTTPAdapter(max_retries = retry)
        s.headers.update(get_token())
#        s.mount('http://', adapter = adatper)
        s.mount(get_url(), adapter = adatper)
#            s.hooks['responce'].append(session_hook)
        for message in message_set:
            data ={
                "id": numpy.int64(message.id), 
                "phone": int(message.clients.phone_number), 
                "text": str(message.sendlist.send_text)
                }
            resp = s.post(f'{get_url()}{numpy.int64(message.id)}', data = data)
            resp_dict[message.id] = resp.status_code
    return try_to_end.delay(cache_key = cache_key, resp_dict = resp_dict)

@shared_task
def try_to_end(cache_key, resp_dict):
    '''Проверяем результат'''
    message_set = get_messages(cache_key)
    for message in message_set:
        if resp_dict.get(str(message.id)) == 200:
            message.status_sent = "Compleate"
            message.date_send =  datetime.now()
        elif timezone.make_naive(message.sendlist.date_end, datetime.strptime(message.clients.time_zone, '%z').tzinfo) >= datetime.now():
            message.date_send =  datetime.now()
            message.status_sent = "in_progres"
        else:
            message.status_sent = f"resp status: {resp_dict.get(str(message.id))}"
    Message.objects.bulk_update(message_set, ['status_sent'])
    message_set = [message for message in message_set if message.status_sent == "in_progres"]
    if message_set != []:
        key = get_cache_key(message_set)
        cache.set(key, message_set, 60*10)
        return send_messages.apply_async(cache_key = key, countdown = 360)
    return
