from django.contrib import admin
from .models import Chatroom

# Register your models here.
admin.site.register(
   Chatroom,
   list_display=["id","room_name"],
   list_display_links=["id","room_name"],
)