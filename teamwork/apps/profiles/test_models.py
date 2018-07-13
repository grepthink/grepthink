"""
Teamwork: test_models.py

Unit tests for models.py: tests all created functions

Usuage: Run a part of all test with `python manage.py test`
"""

from django.test import TestCase
from teamwork.apps.profiles.models import *

# Create your tests here.
class TestDayOfWeek(TestCase):
    """
    Tests various methods included in projects/models.py

    Adapted from: https://docs.djangoproject.com/en/1.11/topics/testing/overview/
    """
    def setUp(self):
        """
        Initialize things here
        """

    def test_day_of_week_basic(self):
        valid_days = [day for day in range(9,16)]
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for i in range(len(valid_days)):
            self.assertEqual(dayofweek(valid_days[i]), days[i])

    def test_day_of_week_invalid(self):
        invalid_days = [8, 16, 'Monday']
        for i in range(len(invalid_days)):
            self.assertEqual(dayofweek(invalid_days[i]), 'Invalid')

    
    
    # Unsure how to test these functions
    
    # def test_validate_image_basic(self):
    #     return(0)
    # def test_create_user_profile(self):
    #     return(0)
    # def test_save_user_profile(self):
    #     return(0)
