"""
Teamwork: test_models.py

Unit tests for models.py: tests all created functions

Usuage: Run a part of all test with `python manage.py test`
"""

from django.test import TestCase
from teamwork.apps.profiles.models import *
from teamwork.apps.profiles.views import *

# Create your tests here.
class TestAlertView(TestCase):
    """
    Tests various methods included in profiles/views.py

    Adapted from: https://docs.djangoproject.com/en/1.11/topics/testing/overview/
    """
    def setUp(self):
        """
        Initialize things here
        """
        # Create a test user as an attribute of TestAlertView, for future use
        #   (we're not testing user or profile methods here)
        self.user1 = User.objects.create_user(
                        'user_test1',
                        'test1@test.com',
                        'groupthink')


    # How to test redirects?
    # https://docs.djangoproject.com/en/dev/topics/testing/tools/
    def test_view_alerts(self):
        response = self.client.get('profiles/alerts.html')
        self.assertEqual(response.status_code, 404)

    # def test_read_alert(self):
    #     return(0)
        
    # def test_unread_alert(self):
    #     return(0)

    # def test_archive_alert(self):
    #     return(0)

    # def test_delete_alert(self):
    #     return(0)

