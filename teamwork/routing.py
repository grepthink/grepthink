from channels import include

channel_routing = [
   include("teamwork.apps.chat.routing.websocket_routing"),
   
   include("teamwork.apps.chat.routing.custom_routing"),
]
