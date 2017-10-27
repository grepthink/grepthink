from channels import route
from .consumers import *

websocket_routing = [
    #Websocket connects
    route("websocket.connect", ws_connect),
    
    #Websocket receives a data frame
    route("websocket.receive", ws_receive),
    
    #Websocket disconnects
    route("websocket_disconnect", ws_disconnect),
]

custom_routing = [
    #Handle different chat commands here,
    #websocket receive routes messages here and goes
    #to the proper place???? In theory, not tested
    route("chat.receive", chat_join, command="^join$"),
    route("chat.receive", chat_leave, command="^leave$"),
    route("chat.receive", chat_send, command="^send$"),
]