import json
from django.db import models
from channels import Group
from django.contrib.auth.models import User
from django.urls import reverse
from teamwork.apps.profiles.models import Alert

#https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
#USE THE LINK ABOVE FOR TIME FORMATS
# Chatroom model which holds the chat room ID and the name
class Chatroom(models.Model):
    #Name of the room
    name = models.CharField(
        max_length = 255,
        default='',
        null=True)
    #The members of the chat
    user = models.ManyToManyField(
        User,
        related_name = 'rooms')

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

        #Holds the message payload
        #Date time format is set as Hours:Minutes AM/PM
        message = {
            'chatroom':str(self.id),
            'message':message,
            'username':user.username,
            'date': text.date.strftime("%I:%M %p")
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

    #Takes in a username and searches for the user, then adds them to the chatroom
    def add_user_to_chat(self,username_token):
        new_user = User.objects.get(username=username_token)
        self.user.add(new_user)
        return

    #Removes the selected user from the chat
    def remove_user(self,user):
        if(self.user.filter(username=user.username).count()>0):
            self.user.remove(user)
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
def send_chat_invite(send_user,receive_user,chatroom):
    Alert.objects.create(
            sender=send_user,
            to=recieve_user,
            msg="You were added to " + chatroom.name,
            url=reverse('view_chats'),
            read=False,
            )

def send_chat_alert(send_user,receive_user,chatroom):
    print("here")
    Alert.objects.create(
            sender=send_user,
            to=receive_user,
            msg="A person wants you to see this in " + chatroom.name,
            url=reverse('view_chats'),
            read=False,
            )

class Chattext(models.Model):

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
