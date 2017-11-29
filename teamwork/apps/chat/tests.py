from django.test import TestCase
from .models import *
from django.contrib.auth.models import User
from teamwork.apps.projects.models import *

# Create your tests here.
class ChatroomTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="testuser1")
        self.user2 = User.objects.create(username="testuser2")
        Chatroom.objects.create(name="testChatroom1")
        project1 = Project.objects.create(
            title="testProject1",
            creator=self.user1,
            scrum_master=self.user2,
            ta=self.user2,
            tagline="Test Tagline 1",
            content="Test Content 1",
            avail_mem=True,
            sponsor=False,
            slug="test1-slug",
            resource="Test Resource 1")
        Membership.objects.create(user=self.user1, project=project1, invite_reason='')

    def test_add_then_delete_chat(self):
        user1 = User.objects.get(username="testuser1")
        user2 = User.objects.get(username="testuser2")
        room = Chatroom.objects.get(name="testChatroom1")
        room.user.add(user1)
        room.user.add(user2)
        room.remove_user(user1)
        room.remove_user(user2)
        self.assertEqual(Chatroom.objects.filter(name="testChatroom1").count(),0)
        
    def project_chat_exists(self):
        project_chat = Chatroom.get_chatroom_with_project("testProject1").count()
        self.assertEqual(project_chat, 0)
    
    
    def project_chat_add_member(self):
        project_chat = Chatroom.get_chatroom_with_project("testProject1")
        self.assertEqual(project_chat.user.objects.all().count(), 1)
        project1 = Project.get_my_projects(self.user1)
        Membership.objects.create(user=self.user2, project=project1, invite_reason='')
        self.assertEqual(project_chat.user.objects.all().count(), 2)
    
    def project_chat_remove_member(self):
        project1 = Project.get_my_projects(self.user1)
        to_delete = Membership.object.filter(user=self.user2, project=project1)
        for mem in to_delete:
            mem.delete()
        chat = Chatroom.get_chatroom_with_project("testProject1")
        self.assertEqual(chat.user.objects.all().count(), 1)   

    def tearDown(self):
        user1 = User.objects.get(username="testuser1")
        user2 = User.objects.get(username="testuser2")
        user1.delete()
        user2.delete()
        if(Chatroom.objects.filter(name="testChatroom1").count()!=0):
            room = Chatroom.objects.get(name="testChatroom1")
            room.delete()
 