from channels.auth import channel_session_user_from_http, channel_session_user
from channels import Channel
import json

import .models

# most of these are not tested, but a good example of the system
# also named like the example t came from
@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({"accept":True})
    message.channel_session['chatrooms'] = []

#no idea what to change here, but something need to be changed
def ws_receive(message):
    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel']
    Channel("chat.receive").send(payload)

#TODO, stuff
@channel_session_user
def ws_disconnect(message):
    for rooms in message.channel_session.get("rooms",set()):
        try:
            room = Chatroom.objects.get(pk=rooms)
            room.websocket_group.discard(message.reply_channel)
        except Room.DoesNotExist:
            pass
        
#assuming logged in, will catch that later
#this is how I assume it should work, rest is like the example
#not tested!
@channel_session_user
def chat_init(message):
    #make self session for one to one server replies
    Group("User:"+str(message.user.id)).add(message.reply_channel)
    #get rooms and add to session
    for room in message.user.rooms.all()
        room.websocket_group.add(message.reply_channel)
        message.reply_channel.send({
            "text": json.dumps({
                "join":str(room.id),
                "name":room.name,
                }).
            })
        #assuming webpages are not multithreaded silliness
        #this should populate the client without http
        for text in room.get_chat():
            send_text_to_one(message.user,text)
        
