from django.contrib import admin
from .models import Chatroom

# Register your models here.
#Registers the chat model into the admin page, really simple right now
#and the only way to add a chat room currently
admin.site.register(
   Chatroom,
   list_display=["id","name"],
   list_display_links=["id","name"],
)