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
from teamwork.apps.profiles.views import view_profile
from teamwork.apps.core.helpers import *
from teamwork.apps.courses.views import view_one_course
from teamwork.apps.profiles.views import view_alerts
from teamwork.apps.chat.models import *

from teamwork.apps.courses.forms import EmailRosterForm
from .forms import *
from .models import *

from itertools import chain
import json



# Create your views here.
def _chats(request, rooms):
    page = request.GET.get('page')

    # Populate with page name and title
    page_name = "My Chats"
    page_description = "Chat List"
    title = "My Chats"

    return render(request, 'chat/chat.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title,
        'rooms': rooms})

@login_required
def view_chats(request):
    #rooms = Chatroom.objects.order_by("name")
    my_rooms = request.user.rooms.all()
    return _chats(request, my_rooms)




@login_required
def view_one_chat(request, slug):
    room = get_object_or_404(Chatroom, name=slug)
    user_rooms = request.user.rooms.all()
    if(room in user_rooms):
        title = "GT Chat"
        page_name = slug
        page_description = "Chatroom"
        name = slug
        user = request.user
        #messages = room.get_chat_init()

        return render(request, 'chat/one_chat.html',{
            'title': title, 'page_name': page_name,
            'page_description' : page_description, 'room': room, 'name': name,
            'user': user})
    else:
        return view_chats(request)

@login_required
def create_chat(request):
    """
    Public method that creates a form and renders the request to create_project.html
    """
    # Populate page info with new project headers/title
    page_name = "Create Chatroom"
    page_description = "Post a new Chatroom"
    title = "Create Chatroom"

    # Get the current user, once and only once.
    user = request.user

    # profile = Profile.objects.get(user=user)
    profile = user.profile

    if request.method == 'POST':
        form = CreateChatForm(user.id, request.POST)
        if form.is_valid():
            room = Chatroom()

            all_rooms = Chatroom.objects.all()
            room.name = form.cleaned_data.get('name')
            for one_room in all_rooms:
                #print(room.name+"\n")
                #print(one_room.name+"\n")
                if room.name == one_room.name:
                    name_error = "Room already exists with that name, choose a unique name"
                    return render(request, 'chat/create_chat.html', {'page_name': page_name,
                        'page_description': page_description, 'title': title, 'form': form, 'name_error': name_error})
            room.save()
            user_input_field = form.cleaned_data.get('user')
            all_usernames = user_input_field.split(", ")
            for name in all_usernames:
                room.add_user_to_chat(name)
            room.save()
            return redirect(view_chats)
        else:
            return redirect(view_chats)
    else:
        form = CreateChatForm(request.user.id)

    name_error = "Choose a unique name"
    return render(request, 'chat/create_chat.html', {'page_name': page_name,
        'page_description': page_description, 'title': title, 'form': form, "name_error": name_error})

@login_required
def invite_chat(request, slug):
    page_name = "Invite to Chatroom"
    page_description = "Invite a user to a Chatroom"
    title = "Invite to Chatroom"
    room = get_object_or_404(Chatroom, name=slug)

    
    # Get the current user, once and only once.
    user = request.user
    
    if request.method == 'POST':
        form = InviteChatForm(user.id, request.POST)
        if form.is_valid():
            #print("Form IS valid")
            user_input_field = form.cleaned_data.get('user')
            all_usernames = user_input_field.split(", ")
            for name in all_usernames:
                room.add_user_to_chat(name)
            room.save()
            return redirect(view_chats)
        else:
            #print("Form IS NOT valid")
            return redirect(view_chats)
    else:
        form = InviteChatForm(request.user.id)

    return render(request, 'chat/invite_chat.html', {'page_name': page_name,
    'page_description': page_description, 'title': title, 'form': form, 'room': room})


@login_required
def leave_chat(request, slug):
    page_name = "Leave Chatroom"
    page_description = "Leave a Chatroom"
    title = "Leave Chatroom"
    room = get_object_or_404(Chatroom, name=slug)

    # Get the current user, once and only once.
    user = request.user
    if request.method == 'POST':
        room.remove_user(user)
        return redirect(view_chats)

    return render(request, 'chat/leave_chat.html', {'page_name': page_name,
        'page_description': page_description, 'title': title, 'room': room})

#Finds if the username exists and returns the page for the user profile
#Assumes that the username is without the @ sign, fk u trevor - trevor
def find_user_profile(request, username, slug):
    #For some reason receives input as {% url 'find_user_profile' @name %}
    #Splits the string and the 4th index is the username
    #[1:] gets everything after the @ sign as the username and searches
    #SHOULD REPLACE THIS IS UGLY AS HELL
    user = username.split(" ")[3][1:]
    if User.objects.filter(username=user).exists():
        return view_profile(request, user)
    return redirect(view_one_chat, slug)
