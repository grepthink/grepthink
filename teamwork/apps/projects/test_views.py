"""
test_views.py

Project app's View Tests

"""

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import UserManager
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from teamwork.apps.courses.models import *
from teamwork.apps.profiles.models import *
from teamwork.apps.projects.models import *
from teamwork.apps.projects.views.EditProjectView import *
from teamwork.apps.projects.views.EditTsrView import *

class ViewProjectTestCase(TestCase):
    """ Tests the view_one_project method in projects/views.py. """
    def setUp(self):
        """
        Initialize project, user, and membership objects for use in test methods.

        # Actually not need in this simple test. But will be useful in other tests.
        # user1 = create_user('user_test1', 'test1@test.com', 'groupthink')
        # Membership.objects.create(user=user1, project=project1, invite_reason='')
        """

    @override_settings(STATICFILES_STORAGE=None)
    def test_view_one_project(self):
        """
        Confirms that view_one_project sucesfully returns a 200 response when given the slug of an
        existing project.

        Decorator override_settings to avoid errors with whitenoise when using client().
        """
        # Create a test user as an attribute of ProjectTestCase, for future use
        #   (we're not testing user or profile methods here)
        # self.user1 = User.objects.create_user('user_test1', 'test1@test.com', 'groupthink')
        #
        # test = authenticate(self, username='user_test1', password='groupthink')
        # login(username='user_test1', password='groupthink')
        # The course is now looked up in view_one_project because it is needed for breadcrumbs.
        # course1 = create_course("Test Course 1", "test-course1", "Test Info")
        # course1 = Course.objects.create(name="Test Course 1", info="Test Course", slug="test-course1",
        #     creator=self.user1)

        # # Create a test project to be served.
        # # Currently can't create_project due to User not being authenticated (logged-in),
        # #
        # project1 = create_project("Test Project 1", self.user1, "Test Tagline 1",
        #     "Test Content 1", "test1-slug", "Test Resource 1")
        #
        # # Add the project to the course many to many field so the course lookup is successful.
        # course1.projects.add(project1)
        #
        # # Get the response using reverse to load the url with keyword arg: slug of project 1
        # response = self.client.get(reverse('view_one_project', kwargs={'slug':project1.slug}))
        #
        # # Confirm that view_one_project returned a response with status code 200 (page served successfully).
        # self.assertEqual(response.status_code, 200)
        pass

class EditProjectTestCase(TestCase):
    def setUp(self):
        # create needed objects
        self.user1 = create_user("test1", "test1@test.com", "test1")
        self.user2 = create_user("test2", "test2@test.com", "test2")
        self.user3 = create_user("test3", "test3@test.com", "test3")
        self.course1 = create_course("course1", "slug1", self.user1)
        self.enrollment1 = create_course_enrollment(self.user1, self.course1, "student")
        self.enrollment2 = create_course_enrollment(self.user2, self.course1, "student")
        self.project1 = create_project(self.user1, self.user1, self.user1, self.course1, "slug1")
        self.membership1 = create_project_membership(self.user1, self.project1, "invite reason")
        self.client = Client()

    # TODO:
    def tearDown(self):
        pass

    # TODO:
    def test_add_member(self):
        """
        - Successfully add a member
        """
        # self.client.login(username='test1', password='test1')
        # response = self.client.get('/project/slug1/add/test2')
        # print("status code: ", response.status_code)
        # print("all projects", Project.objects.all())
        # self.assertTrue(response.status_code == '200')
        pass

    def test_try_add_member_success(self):
        """
        - Successfully adding a member that meets validation to be able to join
        """
        self.client.login(username='test1', password='test1')
        response = self.client.post('/project/slug1/tryadd/test2')

        # Assert redirect was returned
        self.assertTrue(response.status_code == 302)

        # Assert project now has 1 member
        self.assertTrue(self.user2 in self.project1.members.all())

    def test_try_add_member_fail(self):
        """
        - Tests not accepting a member if they are not in the course or already a member
        - Tests project is not accepting members
        """
        self.client.login(username='test1', password='test1')
        response = self.client.post('/project/slug1/tryadd/test3')

        # Assert redirect was returned
        self.assertTrue(response.status_code == 302)

        # Assert user3 was not successfully added (user3 is not enrolled in course1)
        self.assertTrue(self.user3 not in self.project1.members.all())

        # Test project is not accepting members and a member is added
        self.project1.avail_mem = False
        self.project1.save()

        response = self.client.post('/project/slug1/tryadd/test2')
        self.assertTrue(self.user2 not in self.project1.members.all())

class TestEditTsrView(TestCase):
    requestScrum = "WSGIRequest: GET '/project/project-one/tsr/testing123/edit/?scrum_master=scrum_master'"
    requestMember = "WSGIRequest: GET '/project/project-one/tsr/testing123/edit/?'"

    def test_is_scrum_master(self):
        self.assertEqual(is_scrum_master(self.requestScrum), True)

    def test_isnt_scrum_master(self):
        self.assertEqual(is_scrum_master(self.requestMember), False)

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