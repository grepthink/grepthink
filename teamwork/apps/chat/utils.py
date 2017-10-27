from functools import wraps

from .exceptions import ClientError
from .models import Chatroom

def catch_client_error(func):

    @wraps(func)
    def inner(message, args, **kwargs):
        try:
            return func(message, args, **kwargs)
        except ClientError as e:
            e.send_to(message.reply_channel)
    return inner
    
def get_room_or_error(room_id, user):
    #Checks if user is logged in
    if not user.is_authenticated():
        raise ClientError("USER_HAS_TO_LOGIN")
    #Find the room requested by ID
    try:
        room = Chatroom.objects.get(pk=room_id)
    except Chatroom.DoesNotExist:
        raise ClientError("ROOM_INVALID")
    #Check permissions if needed, possibly for secret admin chats
    #Maybe add some other time
    
    
    return room