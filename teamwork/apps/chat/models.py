import json
from django.db import models
from channels import Group
from django.contrib.auth.models import User

# Create your models here.
class Chatroom(models.Model):
    
    name = models.CharField(max_length=255)
    user = models.ManyToManyField(User, related_name='rooms')

    class Meta:
        ordering = ('name',)


    @property
    def websocket_group(self):
        return Group("Room-" +str(self.id))
    
    def send_message(self,message,user):


        #save the text for later
        text = Chattext(room=self,author=user)
        text.content = message
        text.save()
        #a modified version of that one
        #will send a message to all
        message = {'chatroom':str(self.id), 'message':message, 'username':user.username}

        #dumps or dump?
        #dumps!
        self.websocket_group.send(
            {"text":json.dumps(message)}
            )

    #django doesn't have a some() just this thing
    def get_chat_init(self):
        return self.chat.all()[:10]

    #maybe should catch error here, but oh well
    def get_chat_next(self,number):
        return self.chat.all()[number:number+10]

    def __str__(self):
        return self.name

#this isn't the right place for this, so move it later
#also it may be unneeded, but oh well
#send a message to a user
def send_text_to_one(user,chattext):
    message = {'chatroom':str(chattext.room.id),'message':chattext.content, 'username':chattext.author.username}
    Group("User-"+str(user.id)).send(
        {"text":json.dumps(message)}
        )

class Chattext(models.Model):
    
    room = models.ForeignKey(Chatroom, related_name='chat', on_delete=models.CASCADE)
    #need to change this to deleted user later, for now it's fine
    author = models.ForeignKey(User, related_name='author_char', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True,editable=True)
    content = models.CharField(max_length=2000, default="")
        

    class Meta:
        verbose_name = "Project Chat"
        ordering = ("-date", )
        
    def __str__(self):
        return '(0) - (1)'.format(self.author.username, self.content)
    
    


