"""
Teamwork: test_views.py

Unit tests for views.py in app projects.

Usuage: Run as a part of all test with `python manage.py test`
"""

from django.contrib.auth.models import UserManager
# Django Modules
from django.test import TestCase, override_settings
from django.urls import reverse

from teamwork.apps.profiles.models import *
from teamwork.apps.projects.models import *


def create_project(title, creator, tagline, content, slug, resource, avail_mem=True, sponsor=False):
    # Create a dummy project (with no M2M relationships) that will be associated with user1
    return Project.objects.create(title="Test Project 1", creator="user_test1",
        tagline="Test Tagline 1", content="Test Content 1",
        avail_mem=True, sponsor=False, slug="test1-slug",resource="Test Resource 1")

def create_user(username, email, password):
    # Create a test user as an attribute of ProjectTestCase, for future use
    #   (we're not testing user or profile methods here)
    return User.objects.create_user(username, email, password)


class ViewProjectTestCase(TestCase):
    """
    Tests the view_one_project method in projects/views.py

    References: 
    https://docs.djangoproject.com/en/1.11/topics/testing/overview/
    https://docs.djangoproject.com/en/1.11/intro/tutorial05/#testing-our-new-view
    https://docs.djangoproject.com/en/1.11/topics/testing/tools/#django.test.override_settings
    https://docs.djangoproject.com/en/1.11/ref/urlresolvers/#django.core.urlresolvers.reverse
    """
    def setUp(self):
        """
        Initialize project, user, and membership objects for use in test methods.
        """

    @override_settings(STATICFILES_STORAGE = None)
    def test_view_one_project(self):
        """
        Confirms that view_one_project sucesfully returns a 200 response when given the
        slug of an existing project.

        Decorator override_settings to avoid errors with whitenoise.
        """

        # Create a test project to be servered
        project1 = create_project("Test Project 1", "user_test1", "Test Tagline 1", 
            "Test Content 1", "test1-slug", "Test Resource 1")

        # Not used in this test but will be used to test other project views.
        # user1 = create_user('user_test1', 'test1@test.com', 'groupthink')

        # Get the response using reverse to load the url with keyword arg: slug of project 1
        response = self.client.get(reverse('view_one_project', kwargs={'slug':project1.slug}))

        # Confirm that view_one_project returned a response with status code 200 (page served sucesfully).
        self.assertEqual(response.status_code, 200)
