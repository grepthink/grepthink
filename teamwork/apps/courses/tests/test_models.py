"""
test_models.py

Unit tests for models.py: tests all created functions
"""

from django.contrib.auth.models import UserManager
from django.test import TestCase
from teamwork.apps.courses.models import *
from teamwork.apps.profiles.models import *
from teamwork.apps.projects.models import Membership

class CourseTestCase(TestCase):
    """
    Tests various methods included in courses/models.py.

    Adapted from: https://docs.djangoproject.com/en/1.11/topics/testing/overview/
    """
    def setUp(self):
        """Initialize course, user, and enrollment objects for use in test methods."""
        # Create a test user as an attribute of ProjectTestCase, for future use
        #   (we're not testing user or profile methods here)
        self.user1 = create_user('user_test1', 'test1@test.com', 'groupthink')

        # create a dummy course (with no M2M relationships) that will be associated with user1
        self.course1 = create_course('Test Course 1', 'test1-slug', self.user1)
        self.course2 = create_course('Test Course 2', 'test2-slug', self.user1)

        # Create a membership object between user1 and project1
        self.enrollment1 =  create_course_enrollment(self.user1, self.course1, 'professor')
        self.enrollment2 =  create_course_enrollment(self.user1, self.course2, 'professor')
    
    def tearDown(self):
        """ TODO """
        pass

    def test_get_user_courses(self):
        """All courses associated with a user are returned."""
        my_courses = Course.get_my_courses(self.user1)
        self.assertTrue(self.course1 in my_courses)
        self.assertTrue(self.course2 in my_courses)

    def test_get_my_created_courses(self):
        """All created courses associated with a user are returned."""
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

def create_project(creator, scrum_master, ta, course, slug):
    """
    Create a Project helper - Creates a project and adds it to a course

    Args:
        creator: (User) Course Creator
        scrum_master: (User) Project's Scrum Master
        ta: (User) Project's Teacher Assistant
        course: (Course) The Course which the Project will be added to
        slug: (str) The project's slug
    """
    project = Project.objects.create(creator=creator,
                                     scrum_master=scrum_master,
                                     ta=ta,
                                     slug=slug)
    course.projects.add(project)
    course.save()
    return project

def create_user(username, email, password):
    """
    Create a User helper

    Args:
        username: (str) Username of the new user
        email: (str) Email of the new user
        password: (str) Password of the new user
    """    
    return User.objects.create_user(username, email, password)

def create_course(name, slug, creator):
    """
    Create Course helper

    Args:
        name: (str) Course Name
        slug: (str) Course Slug
        creator: (User) Creator of the course
    """
    return Course.objects.create(name=name, slug=slug, creator=creator)

def create_course_enrollment(user, course, role):
    """
    Create Course Enrollment helper

    Args:
        user: (User) User which is being enrolled in the course
        course: (Course) Course which the user is being enrolled in
        role: (str) Expects 'professor' or 'student' or 'ta'
    """
    return Enrollment.objects.create(user=user, course=course, role=role)

def create_project_membership(user, project, invite_reason):
    """
    Create Project Membership helper

    Args:
        user: (User) User which is being enrolled in the project
        project: (Project) Project which the user is becoming a member of
        invite_reason: (str) invite reason ???
    """
    return Membership.objects.create(user=user, project=project, invite_reason=invite_reason)