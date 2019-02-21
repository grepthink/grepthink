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

def create_user(username, email, password):
    return User.objects.create_user(username, email, password)

def create_course(name, slug, creator):
    return Course.objects.create(name=name, slug=slug, creator=creator)

def create_course_enrollment(user, course, role):
    return Enrollment.objects.create(user=user, course=course, role=role)

def create_project_membership(user, project, invite_reason):
    return Membership.objects.create(user=user, project=project, invite_reason=invite_reason)

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
        self.user1 = create_user('user_test1', 'test1@test.com', 'groupthink')

        # create a dummy course (with no M2M relationships) that will be associated with user1
        self.course1 = create_course('Test Course 1', 'test1-slug', self.user1)
        self.course2 = create_course('Test Course 2', 'test2-slug', self.user1)

        # Create a membership object between user1 and project1
        self.enrollment1 =  create_course_enrollment(self.user1, self.course1, 'professor')
        self.enrollment2 =  create_course_enrollment(self.user1, self.course2, 'professor')

    # TODO:
    def tearDown(self):
        pass

    def test_get_user_courses(self):
        """All courses associated with a user are returned"""
        my_courses = Course.get_my_courses(self.user1)
        self.assertTrue(self.course1 in my_courses)
        self.assertTrue(self.course2 in my_courses)

    def test_get_my_created_courses(self):
        """All created courses associated with a user are returned"""
        my_created_courses = Course.get_my_created_courses(self.user1)
        self.assertTrue(self.course1 in my_created_courses)
        self.assertTrue(self.course2 in my_created_courses)

    def test_get_active_courses(self):
        # call get active, initially both courses should be active
        active_courses = get_user_active_courses(self.user1)
        self.assertTrue(self.course1 in active_courses)
        self.assertTrue(self.course2 in active_courses)

        # inactivate course2, ensure course1 is only returned as active
        self.course2.disable = True
        self.course2.save()

        active_courses = get_user_active_courses(self.user1)
        self.assertTrue(self.course1 in active_courses)
        self.assertTrue(self.course2 not in active_courses)

    def test_get_inactive_courses(self):
        # call get inactive, initially neither courses should be inactive
        inactive_courses = get_user_disabled_courses(self.user1)
        self.assertTrue(self.course1 not in inactive_courses)
        self.assertTrue(self.course2 not in inactive_courses)

        # deactivate course2, ensure course2 is only returned as inactive
        self.course2.disable = True
        self.course2.save()

        inactive_courses = get_user_disabled_courses(self.user1)
        self.assertTrue(self.course1 not in inactive_courses)
        self.assertTrue(self.course2 in inactive_courses)

    def test_delete_course(self):
        """
        TODO: once delete is moved to Course model
        """
        pass
