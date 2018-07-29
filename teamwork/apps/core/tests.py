from django.core.urlresolvers import resolve
from django.test import TestCase

from django.contrib.auth.models import User

from teamwork.apps.core.views import *
from teamwork.apps.core.models import EmailAddressAuthBackend

# class MatchPageTest(TestCase):
#     def test_root_url_resolves_to_match_page_view(self):
#         found = resolve('/')
#         self.assertEqual(found.func, index)


class AuthenticateWithEmailTest(TestCase):
    """
    Creates a user and asserts return values are correct from authenticate method
    """
    def setUp(self):
        self.user1 = User.objects.create_user('user_test1', 'test1@test.com', 'groupthink')

    def tearDown(self):
        del self.user1

    def testAuthenticateSuccess(self):
        """
        Attempt to authenticate user w/ correct email address and pw and assert user object is returned
        """
        user = EmailAddressAuthBackend.authenticate(self, username='test1@test.com', password='groupthink')
        self.assertTrue(type(user) is User)

    def testAuthenticateFail(self):
        """
        Attempt to authenticate user w/ incorrect password and assert user object is None
        """
        user = EmailAddressAuthBackend.authenticate(self, username='test1@test.com', password='incorrect')
        self.assertIsNone(user)
