from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/socket-server/', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/race-server/', consumers.RaceConsumer.as_asgi()),
    re_path(r'ws/racestudent-server/', consumers.RaceStudentConsumer.as_asgi()),
    re_path(r'ws/sign-server/', consumers.SignConsumer.as_asgi()),
    re_path(r'ws/group-server/', consumers.GroupConsumer.as_asgi())
]
