"""
Teamwork: test_models.py

Unit tests for models.py: tests all created functions

Usuage: Run a part of all test with `python manage.py test`
"""

from django.contrib.auth.models import UserManager
# Django Modules
from django.test import TestCase

from teamwork.apps.profiles.models import *
from teamwork.apps.projects.models import *


class ProjectTestCase(TestCase):
    """
    Tests various methods included in projects/models.py

    Adapted from: https://docs.djangoproject.com/en/1.11/topics/testing/overview/
    """
    def setUp(self):
        """
        Initialize project, user, and membership objects for use in test methods.
        """
        # Create a test user as an attribute of ProjectTestCase, for future use
        #   (we're not testing user or profile methods here)
        self.user1 = User.objects.create_user(
                        'user_test1',
                        'test1@test.com',
                        'groupthink')

        self.user2 = User.objects.create_user(
                        'user_test2',
                        'test2@test.com',
                        'groupthink2')

        # Create a dummy project (with no M2M relationships) that will be associated with user1
        project1 = Project.objects.create(
                        title="Test Project 1",
                        creator=self.user1,
                        scrum_master=self.user2,
                        ta=self.user2,
                        tagline="Test Tagline 1",
                        content="Test Content 1",
                        avail_mem=True,
                        sponsor=False,
                        slug="test1-slug",
                        resource="Test Resource 1")

        # Create a membership object between user1 and project1
        Membership.objects.create(user=self.user1, project=project1, invite_reason='')

    def test_get_my_projects(self):
        """All projects associated with a user are returned"""
        my_projects = Project.get_my_projects(self.user1)
        for proj in my_projects:
            # Test fails if any unexpected project slug is returned.
            self.assertEqual(proj.slug, 'test1-slug')

    def test_get_all_projects(self):
        """All projects in the database"""
        all_projects = Project.get_all_projects()
        # Test fails if there is not 1 projects in the test DB
        self.assertEqual(len(all_projects), 1)

    def test_get_created_projects(self):
        created_projects = Project.get_created_projects(self.user1)
        for proj in created_projects:
            self.assertEqual(proj.creator, self.user1)
