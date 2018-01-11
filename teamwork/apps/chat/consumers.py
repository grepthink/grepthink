from channels.auth import channel_session_user_from_http, channel_session_user
from channels import Channel
from channels.auth import channel_session_user_from_http, channel_session_user
from .models import *
from .utils import *
import json
import hashlib



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

    chat_messages = room.get_chat_init()
    messages = []
    for index in range(len(chat_messages)-1,-1,-1):
        text = {
            'chatroom':str(chat_messages[index].room.id),
            'message':chat_messages[index].content,
            'username':chat_messages[index].author.username,
            'date':chat_messages[index].date.strftime("%I:%M %p"),
            'gravitar':hashlib.md5(chat_messages[index].author.email.lower().encode('utf-8')).hexdigest()
            }
        messages.append(text)
    send_texts_to_one(message.user, messages)

@channel_session_user
@catch_client_error
def chat_send_old(message):
    room = get_room_or_error(message["room"],message.user)
    chat_messages = room.get_chat_next(message["number"])
    messages = []
    for index in range(0,len(chat_messages)):
        text = {
            'chatroom':str(chat_messages[index].room.id),
            'message':chat_messages[index].content,
            'username':chat_messages[index].author.username,
            'date':chat_messages[index].date.strftime("%I:%M %p"),
            'gravitar':hashlib.md5(chat_messages[index].author.email.lower().encode('utf-8')).hexdigest()
            }
        messages.append(text)
    send_oldtexts_to_one(message.user, messages)
#same as join, but more reliable for multiple rooms
@channel_session_user
@catch_client_error
def chat_join_multiple(message):
    roomArray = []
    messagesArray = []
    for roomNumber in message["rooms"]:
        room = get_room_or_error(roomNumber,message.user)
        room.websocket_group.add(message.reply_channel)
        message.channel_session['rooms'] = list(
            set(message.channel_session['chatrooms'])
            .union([room.id]))
        text = {
            'join':str(room.id),
            'title': room.name
            }
        roomArray.append(text)
        chat_messages = room.get_chat_init()
        for index in range(len(chat_messages)-1,-1,-1):
            text = {
                'chatroom':str(chat_messages[index].room.id),
                'message':chat_messages[index].content,
                'username':chat_messages[index].author.username,
                'date':chat_messages[index].date.strftime("%I:%M %p"),
                'gravitar':hashlib.md5(chat_messages[index].author.email.lower().encode('utf-8')).hexdigest()
            }
            messagesArray.append(text)
    send_rooms_to_one(message.user,roomArray,messagesArray)



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
    #temp disabling
    #if int(message['room']) not in message.channel_session['rooms']:
    #    raise ClientError("ROOM_ACCESS_DENIED")
    room = get_room_or_error(message["room"], message.user)
    room.send_message(message["message"], message.user)
