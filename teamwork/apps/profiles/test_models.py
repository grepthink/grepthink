"""
Teamwork: test_models.py

Unit tests for models.py: tests all created functions

Usuage: Run a part of all test with `python manage.py test`
"""

from django.test import TestCase
from teamwork.apps.profiles.models import *

# Create your tests here.
class TestSomthing(TestCase):
    """
    Tests various methods included in projects/models.py

    Adapted from: https://docs.djangoproject.com/en/1.11/topics/testing/overview/
    """
    def setUp(self):
        """
        Initialize things here
        """
        valid_days = [day for day in range(9,16)]
        invalid_days = [8, 16, 'Monday']

    def test_day_of_week_basic(self):
        days = ['Sunday', 'Monday', 'Teusday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for i in range(len(valid_days)):
            self.assertEqual(dayofweek(valid_days(i), days(i)))

    def test_day_of_week_invalid(self):
        for i in range(len(invalid_days)):
            self.assertEqual(dayofweek(valid_days(i), 'Invalid'))

    def test_validate_image_basic(self):
        return(0)
    def test_create_user_profile(self):
        return(0)
    def test_save_user_profile(self):
        return(0)
