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
        print("Test case setup!")

    def test_day_of_week_basic(self):
        self.assertEqual(dayofweek(9), "Sunday")