from django.test import TestCase
from .models import *
from django.contrib.auth.models import User

# Create your tests here.
class ChatroomAddAndDelete(TestCase):
    def setUp(self):
        User.objects.create(username="testuser1")
        User.objects.create(username="testuser2")
        Chatroom.objects.create(name="testChatroom1")

    def test_add_then_delete_chat(self):
        user1 = User.objects.get(username="testuser1")
        user2 = User.objects.get(username="testuser2")
        room = Chatroom.objects.get(name="testChatroom1")
        room.user.add(user1)
        room.user.add(user2)
        room.remove_user(user1)
        room.remove_user(user2)
        self.assertEqual(Chatroom.objects.filter(name="testChatroom1").count(),0)

    def tearDown(self):
        user1 = User.objects.get(username="testuser1")
        user2 = User.objects.get(username="testuser2")
        user1.delete()
        user2.delete()
        if(Chatroom.objects.filter(name="testChatroom1").count()!=0):
            room = Chatroom.objects.get(name="testChatroom1")
            room.delete()
