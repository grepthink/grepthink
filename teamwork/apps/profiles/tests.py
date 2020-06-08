from django.test import TestCase
from django.contrib.auth.models import User

from teamwork.apps.profiles.views.BaseView import find_available_username

# Create your tests here.
class DuplicateSignUpTest(TestCase):
    """
    Creates a user and asserts return values are correct from authenticate method
    """
    def setUp(self):
        """
        Init any variables that are needed for testing
        """
        self.user1 = User.objects.create_user('test', 'test@testing.com', 'pw')

    def tearDown(self):
        """
        Delete any variables that were created for testing
        """
        del self.user1

    def test_next_available_username(self):
        """
        Attempt to authenticate user w/ correct email address and pw and assert user object is returned
        """
        # Find the next available username
        next_username = find_available_username("test")

        # assert it is test1
        self.assertTrue(next_username == "test1")

        # create that user w/ username test1
        self.user2 = User.objects.create_user('test1', 'test@another.com', 'pw')

        # next iteration should find that the next avail username is test2
        next_username = find_available_username("test")
        
        # assert it is test2
        self.assertTrue(next_username == "test2")