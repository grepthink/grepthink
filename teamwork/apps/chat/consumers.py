from channels.auth import channel_session_user_from_http, channel_session_user
from channels import Channel
from channels.auth import channel_session_user_from_http, channel_session_user
from .models import *
from .utils import *
import json




# most of these are not tested, but a good example of the system
# also named like the example t came from
@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({'accept':True})
    Group("User-"+str(message.user.id)).add(message.reply_channel)
    message.channel_session['chatrooms'] = []
    

#no idea what to change here, but something need to be changed
#Basically unloads the message payload for now and sends it into the chat
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
#not tested! maybe not used
@channel_session_user
def chat_init(message):
    #make self session for one to one server replies
    Group("User-"+str(message.user.id)).add(message.reply_channel)
    #get rooms and add to session
    for room in message.user.rooms.all():
        room.websocket_group.add(message.reply_channel)
        message.reply_channel.send({
            "text": json.dumps({
                "join":str(room.id),
                "name":room.name,
                })
            })
        #assuming webpages are not multithreaded silliness
        #this should populate the client without http
        for text in room.get_chat():
            send_text_to_one(message.user,text)

#funtion to make a chat name,
# need to discuss what to JSON
def chat_make(message):
    room = Chatroon(name=message["name"])
    room.save()
    message.user.rooms.add(room)
    room.websocket_group.add(message.reply_channel)
    message.reply_channel.send({
            "text": json.dumps({
                "join":str(room.id),
                "name":room.name,
            })
        })


#Looks similir to chat_init, might be the same thing
#Should test this to find out, and ask Hugh what its supposed to do

@channel_session_user
@catch_client_error
def chat_join(message):
    room = get_room_or_error(message["room"],message.user)
    message.user.rooms.add(room)

    room.websocket_group.add(message.reply_channel)
    message.channel_session['rooms'] = list(
        set(message.channel_session['chatrooms'])
        .union([room.id]))
        
    message.reply_channel.send({
        "text": json.dumps({
            "join": str(room.id),
            "title": room.name,
        }),
    })
    for index in range(9,0,-1):
        send_text_to_one(message.user, room.get_chat_init()[index])
    """
    for text in room.get_chat_init():
        send_text_to_one(message.user,text)
    """
    
@channel_session_user
@catch_client_error
def chat_leave(message):
    room = get_room_or_error(message["room"],message.user)
    
    message.user.rooms.remove(room)
    room.websocket_group.discard(message.reply_channel)
    message.channel_session['rooms'] = list(
        set(message.channel_session['rooms'])
        .difference([room.id]))
        
    message.reply_channel.send({
        "text": json.dumps({
            "leave": str(room.id),
        }),
    })
    
@channel_session_user
@catch_client_error
def chat_send(message):
    if int(message['room']) not in message.channel_session['rooms']:
        raise ClientError("ROOM_ACCESS_DENIED")
    room = get_room_or_error(message["room"], message.user)
    room.send_message(message["message"], message.user)
