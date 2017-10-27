from django.contrib import messages
from django.contrib.auth.decorators import login_required
from teamwork.apps.courses.models import *
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.urls import reverse

from teamwork.apps.core.models import *
from teamwork.apps.courses.models import *
from teamwork.apps.profiles.models import Alert
from teamwork.apps.core.helpers import *
from teamwork.apps.courses.views import view_one_course
from teamwork.apps.profiles.views import view_alerts
from teamwork.apps.chat.models import *

from teamwork.apps.courses.forms import EmailRosterForm
#from .forms import *
from .models import *

from itertools import chain
import json



# Create your views here.
def view_chats(request):
    chat_rooms = Chatroom.objects.order_by("room_name")
    title = "Chat"
    
    return render(request,'chat/chat.html',{
        "rooms": chat_rooms, 'title': title})
"""
def _chats(request, chats):
    page = request.GET.get('page')

    # Populate with page name and title
    page_name = "My Chats"
    page_description = "Chat List"
    title = "My Chats"


    return render(request, 'projects/view_chats.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title,
        'chats': chats})

@login_required
def view_chats(request):
    my_chats = Chat.get_my_chats(request.user)

    return _chats(request, my_chats)

@login_required
def view_one_chat(request, slug):
    chat = get_object_or_404(Chat, slug=slug)
    messages 
    return render

"""
