from channels import include

channel_routing = [
   include("teamwork.apps.chat.routing.websocket_routing", path=r"^/chat/stream"),
   
   include("teamwork.apps.chat.routing.custom_routing"),
]