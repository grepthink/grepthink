import json
from django.contrib import auth
from django.db import models
from channels import Group
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from teamwork.apps.profiles.models import Alert
import hashlib

#https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
#USE THE LINK ABOVE FOR TIME FORMATS


# Chatroom model which holds the chat room ID and the name
class Chatroom(models.Model):
    """
    Chatroom: Datbase model for chatrooms

    Fields:
        name: the name of the chatroom.
        user: the users in the chatroom.
        hasProject: if a chatroom is connected to a project
    """
    #Name of the room
    name = models.CharField(
        max_length = 255,
        default='',
        null=True)
    #The members of the chat
    user = models.ManyToManyField(
        User,
        related_name = 'rooms')

    hasProject = models.BooleanField(
        default = False)

    isDirectMessage = models.BooleanField(
        default = False)

    class Meta:
        ordering = ('name',)

    @property
    def websocket_group(self):
        return Group("Room-" +str(self.id))

    #Saves the Chattext model with metadata and sends the payload to the websocket
    def send_message(self,message,user):

        text = Chattext(room=self,author=user)
        text.content = message
        text.save()

        #sends an alert on @
        if '@' in message:
            for substring in (message.split(' ')):
                if substring.startswith('@'):
                    pointed_user = substring[1:]
                    try:
                        User.objects.get(username=user)
                        send_chat_alert(user,User.objects.get(username=pointed_user),self)
                    except ObjectDoesNotExist:
                        continue



        #Holds the message payload
        #Date time format is set as Hours:Minutes AM/PM
        message = {
            'chatroom':str(self.id),
            'message':message,
            'username':user.username,
            'date': text.date.strftime("%I:%M %p"),
            'gravitar':hashlib.md5(user.email.lower().encode('utf-8')).hexdigest()
            
            }

        #Sends the message payload
        self.websocket_group.send(
            {
                "text":json.dumps(message)
            })


    #When a chat is initially loaded, gets the last 10 messages saved, in theory.
    #Called from consumers
    def get_chat_init(self):
        return self.chat.all()[:10]

    #maybe should catch error here, but oh well
    def get_chat_next(self,number):
        return self.chat.all()[number:number+10]

    #Find a chatroom by name only, returns a chatroom or None
    def get_chatroom_by_name(self, room_name):
        try:
            chatroom = Chatroom.objects.get(name=room_name)
            return chatroom
        except ObjectDoesNotExist:
            return None

    def get_chatroom_with_project(self, room_name):
        try:
            chatroom = Chatroom.objects.get(name=room_name,hasProject=True)
            return chatroom
        except ObjectDoesNotExist:
            return None

    def get_chatroom_by_id(self, room_id):
        try:
            chatroom = Chatroom.objects.get(id=room_id)
            return chatroom
        except ObjectDoesNotExist:
            return None


    #Takes in a username and searches for the user, then adds them to the chatroom
    def add_user_to_chat(self,sender,username_token):
        if User.objects.filter(username=username_token).exists():
            new_user = User.objects.get(username=username_token)
            send_chat_invite(sender,new_user,self)
            self.user.add(new_user)
            self.save()
        return

    #Removes the selected user from the chat
    def remove_user(self,user):
        if(self.user.filter(username=user.username).count()>0):
            self.user.remove(user)
            self.save()
        if(self.user.all().count()==0):
            self.delete()
        return

    def __str__(self):
        return self.name

#When a user loads a room this sends the saved messages in the database
def send_text_to_one(user,chattext):
    message = {
        'chatroom':str(chattext.room.id),
        'message':chattext.content,
        'username':chattext.author.username,
        'date': chattext.date.strftime("%I:%M %p")
        }
    Group("User-"+str(user.id)).send(
        {
            "text":json.dumps(message)}
        )
#When a user loads a room this sends the saved messages in the database
def send_texts_to_one(user,messages):
    Group("User-"+str(user.id)).send(
        {
            "text":json.dumps({'messages':messages})}
        )
#should remove repetition
def send_oldtexts_to_one(user,messages):
    Group("User-"+str(user.id)).send(
        {
            "text":json.dumps({'oldmessages':messages})}
        )

def send_rooms_to_one(user,rooms,messages):
    Group("User-"+str(user.id)).send(
        {
            "text":json.dumps({'rooms':rooms,
                               'messages':messages})}
        )

#alert functions
def send_chat_invite(send_user,recieve_user,chatroom):
    Alert.objects.create(
            sender=send_user,
            to=recieve_user,
            msg="You were added to " + chatroom.name,
            url=reverse('view_chats'),
            read=False,
            )

def send_chat_alert(send_user,receive_user,chatroom):
    Alert.objects.create(
            sender=send_user,
            to=receive_user,
            msg="A person wants you to see this in " + chatroom.name,
            url=reverse('view_chats'),
            read=False,
            )

def send_chat_simple(user, user2):
    Alert.objects.create(
            sender=user2,
            to=user,
            msg="A person wants you to see this in one of your chats",
            url=reverse('view_chats'),
            read=False,
            )

#Gets all the chatrooms a user is in
#Used for loading all the chatrooms a user is in on the side tab
def get_user_chatrooms(self):
    return Chatroom.objects.filter(user=self)

auth.models.User.add_to_class('get_user_chatrooms', get_user_chatrooms)


class Chattext(models.Model):
    """
    Chattext: Holds the text messages sent in a chatroom.

    FIelds:
        room: The chatroom the message belongs in.
        author: The user who sent the message.
        date: The time the message was sent.
        content: The message content the user sends.
    """
    room = models.ForeignKey(
        Chatroom,
        related_name='chat',
        on_delete=models.CASCADE)

    #need to change this to deleted user later, for now it's fine
    author = models.ForeignKey(
        User,
        related_name='author_char',
        on_delete=models.CASCADE)

    date = models.DateTimeField(
        auto_now_add=True,
        editable=True)

    content = models.CharField(
        max_length=2000,
        default="")


    class Meta:
        verbose_name = "Project Chat"
        ordering = ("-date", )

    def __str__(self):
        return '(0) - (1) - (2)'.format(self.author.username, self.content)

#because of Django limitation, you must change isdirectmessage to true on creation
class DirectMessage(Chatroom):

    @property
    def websocket_group(self):
        return Group("DM-" +str(self.id))

    #does nothing, and should do nothing
    def add_user_to_chat(self,sender,username_token):
        return

    #removing a user is deleting everything
    def remove_user(self,user):
        self.delete()
        return
