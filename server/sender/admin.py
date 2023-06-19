from django.contrib import admin
from .models import SendList, Clients, Message

@admin.register(SendList)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_start', 'send_text', 'filter', 'date_end']
    list_filter = ['id', 'date_start', 'filter', 'date_end' ]
    
@admin.register(Clients)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number', 'phone_code', 'tags']
    list_filter = ['id', 'phone_number', 'phone_code' ]
    
@admin.register(Message)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_send', 'status_sent', 'clients', 'sendlist']
    list_filter = ['id', 'date_send', 'status_sent']

