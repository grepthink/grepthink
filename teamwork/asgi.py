import os
import channels.asgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "teamwork.settings")
channel_layer = channels.asgi.get_channel_layer()