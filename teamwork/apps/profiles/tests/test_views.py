"""Profile View Test"""
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from teamwork.apps.profiles.models import Profile, Alert

class AlertViewsTests(TestCase):
    """
    Tests 200 status Code returned for static pages:
        - Alert Views
    """
    def setUp(self):
        """ Set Up """
        # Create Test User
        self.user1 = create_user("test1", "test1@test.com", "test1")
        self.user1.save()

        #Create Test Alerts
        self.alert1 = Alert.objects.create(sender=self.user1, to=self.user1)
        self.alert1.save()
        self.alert2 = Alert.objects.create(sender=self.user1, to=self.user1)
        self.alert2.save()

        # Init Client
        self.client = Client()
        self.client.login(username='test1', password='test1')

    def tearDown(self):
        """ Tear Down """
        del self.client

    def test_view_alerts(self):
        """ Test Alerts Page """
        response = self.client.get(reverse('view_alerts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/alerts.html')

    def test_read_alerts(self):
        """ Test Read Alert """
        response = self.client.get(reverse('read_alert', kwargs={'ident': self.alert1.id}))
        self.assertEqual(response.status_code, 302)
        alert = Alert.objects.get(id=self.alert1.id)
        self.assertEqual(alert.read, True)

    def test_unread_alerts(self):
        """ Test Unread Alert """
        response = self.client.get(reverse('unread_alert', kwargs={'ident': self.alert1.id}))
        self.assertEqual(response.status_code, 302)
        alert = Alert.objects.get(id=self.alert1.id)
        self.assertEqual(alert.read, False)

    def test_archive_alerts(self):
        """ Test Archive alerts """
        response = self.client.get(reverse('archive_alerts'))
        self.assertEqual(response.status_code, 302)
        alert = Alert.objects.get(id=self.alert1.id)
        self.assertEqual(alert.read, True)
        alert2 = Alert.objects.get(id=self.alert2.id)
        self.assertEqual(alert2.read, True)

    def test_delete_alerts(self):
        """ Test Archive alerts """
        self.client.get(reverse('read_alert', kwargs={'ident': self.alert1.id}))
        response = self.client.get(reverse('delete_alert', kwargs={'ident': self.alert1.id}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(not Alert.objects.filter(id=self.alert1.id).exists())

class SignupTests(TestCase):
    """SignUp Tests"""

    def setUp(self):
        """Set Up"""
        self.client = Client()

    def tearDown(self):
        """ Tear Down """
        del self.client

    def test_signup_post(self):
        """ Test signup post"""
        data = {'email': 'test1@test1.com', 'password': 'test1', 'confirm_password': 'test1'}
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email=data['email']).exists())
        user = User.objects.get(email=data['email'])
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_signup_get(self):
        """ Test signup get"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/signup.html')

class ProfSignupTests(TestCase):
    """ProfSignUp Tests"""

    def setUp(self):
        """Set Up"""
        self.client = Client()

    def tearDown(self):
        """ Tear Down """
        del self.client

    def test_profsignup_post(self):
        """ Test profsignup post"""
        data = {'email': 'test1@test1.com', 'password': 'test1', 'confirm_password': 'test1'}
        response = self.client.post(reverse('profSignup'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email=data['email']).exists())
        user = User.objects.get(email=data['email'])
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_profsignup_get(self):
        """ Test signup get"""
        response = self.client.get(reverse('profSignup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/professorSignup.html')

def create_user(username, email, password):
    """
    Create a User helper
    Args:
        username: (str) Username of the new user
        email: (str) Email of the new user
        password: (str) Password of the new user
    """
    return User.objects.create_user(username, email, password)

