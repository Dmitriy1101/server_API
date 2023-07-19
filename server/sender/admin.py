from django.contrib import admin
from .models import SendList, Clients, Message

@admin.register(SendList)
class SendListAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_start', 'send_text', 'filters', 'date_end']
    list_filter = ['id', 'date_start', 'filters', 'date_end' ]
    list_display_links = ['date_start',]
    
@admin.register(Clients)
class ClientsAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number', 'phone_code', 'tags', 'time_zone']
    list_filter = ['id', 'phone_number', 'phone_code' ]
    list_display_links = ['phone_number',]
    
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_send', 'status_sent', 'clients', 'sendlist']
    list_filter = ['id', 'date_send', 'status_sent']
    list_display_links = ['date_send',]

