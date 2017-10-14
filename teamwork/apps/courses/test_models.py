"""
Teamwork: test_models.py

Unit tests for models.py: tests all created functions

Usuage: Run a part of all test with `python manage.py test`
"""

from django.contrib.auth.models import UserManager
# Django Modules
from django.test import TestCase

from teamwork.apps.courses.models import *
from teamwork.apps.profiles.models import *


class CourseTestCase(TestCase):
    """
    Tests various methods included in courses/models.py

    Adapted from: https://docs.djangoproject.com/en/1.11/topics/testing/overview/
    """
    def setUp(self):
        """
        Initialize course, user, and enrollment objects for use in test methods.
        """
        # Create a test user as an attribute of ProjectTestCase, for future use
        #   (we're not testing user or profile methods here)
        self.user1 = User.objects.create_user('user_test1', 'test1@test.com', 'groupthink')

        # create a dummy course (with no M2M relationships) that will be associated with user1
        course1 = Course.objects.create(name="Test Course", info="Testing course", slug="test1-slug",
            creator=self.user1)        

        # Create a membership object between user1 and project1
        Enrollment.objects.create(user=self.user1, course=course1)

    def test_get_user_courses(self):
        """All courses associated with a user are returned"""
        my_courses = Course.get_my_courses(self.user1)
        for c in my_courses:
            # Test fails if any unexpected course name is returned.
            self.assertEqual(c.name, 'Test Course')
    def test_get_my_created_courses(self):
        """All created courses associated with a user are returned"""
        my_created_courses = Course.get_my_created_courses(self.user1)
        for c in my_created_courses:
            # Test fails if any unexpected course name is returned
            self.assertEqual(c.name, 'Test Course')
