"""
Core App View Tests
"""

from django.conf import settings
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from teamwork.apps.core.helpers import send_email

class CoreViewsTests(TestCase):
    """
    Tests 200 status Code returned for static pages:
        - About
        - Contact
        - Landing
        - Login (Unauthorized)
        - Login (Authorized)
    """
    def setUp(self):
        # Create Test User
        self.user1 = create_user("test1", "test1@test.com", "test1")

        # Create Test Prof
        self.prof1 = create_user("prof1", "prof1@test.com", "prof1")
        self.prof1.profile.isProf = True
        self.prof1.save()

        # Init Client
        self.client = Client()

    def tearDown(self):
        del self.client

    def test_view_about(self):
        """ Test About Page """
        response = self.client.get(reverse('about'))
        self.assertTrue(response.status_code == 200)
        self.assertTemplateUsed(response, 'core/about.html')
        self.assertContains(response, 'About Grepthink')

    def test_view_contact(self):
        """ Test Contact Page """
        response = self.client.get(reverse('contact'))
        self.assertTrue(response.status_code == 200)
        self.assertTemplateUsed(response, 'core/contact.html')
        self.assertContains(response, 'Contact Grepthink')

    def test_view_landing(self):
        """ Test Landing Page """
        response = self.client.post('/')
        self.assertTrue(response.status_code == 200)
        self.assertTemplateUsed(response, 'core/landing.html')
        self.assertContains(response, 'Join Grepthink')

    def test_view_login_unauth(self):
        """ Test Login View as Unauthorized User """
        response = self.client.get('/login')
        self.assertTrue(response.status_code == 200)
        self.assertTemplateUsed(response, 'core/login.html')
        self.assertContains(response, 'Login');

    def test_view_login_auth(self):
        """ Test Login View as Authorized User """
        self.client.login(username='test1', password='test1')
        response = self.client.post('/login')
        self.assertTrue(response.status_code == 200)
        self.assertTemplateUsed(response, 'core/index.html')
        self.assertContains(response, 'Recent Updates from Courses and Projects');

    def test_view_landing_as_prof(self):
        """ Test Landing as Professor renders Dashboard """
        self.client.login(username='prof1', password='prof1')
        response = self.client.post('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')
        self.assertContains(response, 'Instructor Control Panel')

class EmailTests(TestCase):
    """
    TODO: adjust send_email to be more testable
    """
    def setUp(self):
        self.user1 = create_user("test1", "test1@test.com", "test1")
        self.recipient1 = create_user("recipient1", "recipient1@test.com", "recipient1")
        self.recipient2 = create_user("recipient2", "recipient2@test.com", "recipient2")

    def tearDown(self):
        del self.user1
        del self.recipient1
        del self.recipient2
    
    def test_norecipients_found(self):
        empty_list = []
        response = send_email(empty_list, "gtemail@test.com", "test_norecipients_found", "email content")
        self.assertTrue(response.content.decode("utf-8") == 'No recipients were found.')

    def test_single_recipient(self):
        response = send_email(self.recipient1, "gtemail@test.com", "test_single_recipient", "email content")
        self.assertTrue(response.content.decode("utf-8") == 'Email Sent!')

    def test_successful_recipientlist(self):
        recipient_list = []
        recipient_list.append(self.recipient1)
        recipient_list.append(self.recipient2)
        response = send_email(recipient_list, "gtemail@test.com", "test_single_recipient", "email content")
        self.assertTrue(response.content.decode("utf-8") == 'Email Sent!')

    def test_successful_emaillist(self):
        recipient_list = []
        recipient_list.append(self.recipient1.email)
        recipient_list.append(self.recipient2.email)
        response = send_email(recipient_list, "gtemail@test.com", "test_single_recipient", "email content")
        self.assertTrue(response.content.decode("utf-8") == 'Email Sent!')

    def test_bad_request(self):
        response = send_email(724, "gtemail@test.com", "test_bad_request", "email content")
        self.assertTrue(response.content.decode("utf-8") == 'Bad Request')

class ParseCsvTests(TestCase):
    """
    TODO: Create these tests
    """
    def setUp(self):
        self.csv_path = settings.PROJECT_DIR
        pass

    def tearDown(self):
        pass

def create_user(username, email, password):
    """
    Create a User helper

    Args:
        username: (str) Username of the new user
        email: (str) Email of the new user
        password: (str) Password of the new user
    """    
    return User.objects.create_user(username, email, password)