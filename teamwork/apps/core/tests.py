from django.core.urlresolvers import resolve
from django.test import TestCase, Client

from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from teamwork.apps.core.views import *
from teamwork.apps.core.models import EmailAddressAuthBackend, po_match, sort, auto_ros, by_schedule
from teamwork.apps.core.helpers import *

from teamwork.apps.profiles.models import *
from teamwork.apps.projects.models import *
from teamwork.apps.courses.models import *

def create_project(creator, scrum_master, ta, course, slug):
    project = Project.objects.create(creator=creator,
                                  scrum_master=scrum_master,
                                  ta=ta,
                                  slug=slug)
    course.projects.add(project)
    course.save()
    return project

def create_user(username, email, password):
    # Create a test user as an attribute of ProjectTestCase, for future use
    #   (we're not testing user or profile methods here)
    return User.objects.create_user(username, email, password)

def create_course(name, slug, creator):
    return Course.objects.create(name=name, slug=slug, creator=creator)

def create_course_enrollment(user, course, role):
    return Enrollment.objects.create(user=user, course=course, role=role)

def create_project_membership(user, project, invite_reason):
    return Membership.objects.create(user=user, project=project, invite_reason=invite_reason)

class AuthenticateWithEmailTest(TestCase):
    """
    Creates a user and asserts return values are correct from authenticate method
    """
    def setUp(self):
        """
        Init any variables that are needed for testing
        """
        self.user1 = User.objects.create_user('user_test1', 'test1@test.com', 'groupthink')

    def tearDown(self):
        """
        Delete any variables that were created for testing
        """
        del self.user1

    def testAuthenticateSuccess(self):
        """
        Attempt to authenticate user w/ correct email address and pw and assert user object is returned
        """
        user = EmailAddressAuthBackend.authenticate(self, username='test1@test.com', password='groupthink')
        self.assertTrue(type(user) is User)

    def testAuthenticateFail(self):
        """
        Attempt to authenticate user w/ incorrect password and assert user object is None
        """
        user = EmailAddressAuthBackend.authenticate(self, username='test1@test.com', password='incorrect')
        self.assertIsNone(user)

class FindProjectMatchesTest(TestCase):
    """
    Tests for the po_match method
    """
    def setUp(self):
        """
        Init any variables that are needed for testing
        """
        # create users
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'testing')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'testing')
        self.user3 = User.objects.create_user('user3', 'user3@test.com', 'testing')

        # create course
        self.course = Course.objects.create(name='TestCourse',slug='Test1', creator=self.user1)

        # create enrollment objects
        # user1 is the professor, user2 and user3 are students
        self.enrollment1 = Enrollment.objects.create(user=self.user1, course=self.course, role='professor')
        self.enrollment2 = Enrollment.objects.create(user=self.user2, course=self.course, role='student')
        self.enrollment3 = Enrollment.objects.create(user=self.user3, course=self.course, role='student')

        # user1 create project
        self.project = Project.objects.create(creator=self.user1,
                                              scrum_master=self.user1,
                                              ta=self.user1,
                                              slug='TestCourse1')

        # add project to course
        self.course.projects.add(self.project)

        # create skills that the project will desire
        self.skill1 = Skills.objects.create(skill='SkillOne')
        self.skill2 = Skills.objects.create(skill='SkillTwo')

        # add skill1 to profile2 known skills
        self.user2.profile.known_skills.add(self.skill1)

        # add skill2 to profile3 known skills
        self.user3.profile.known_skills.add(self.skill2)

        # user2 and 3 show interest in created project
        self.interest1 = Interest.objects.create(user=self.user2, interest=5, interest_reason='five')
        self.interest2 = Interest.objects.create(user=self.user3, interest=4, interest_reason='four')

        self.project.interest.add(self.interest1)
        self.project.interest.add(self.interest2)

    def tearDown(self):
        """
        Delete any variables that were created for testing
        """
        # delete users
        del self.user1
        del self.user2
        del self.user3

        # delete project
        del self.project

        # delete skills
        del self.skill1
        del self.skill2

        # delete course
        del self.course

        # delete interest
        del self.interest1
        del self.interest2

    def testMatchWithoutScheduleBonus(self):
        """
        Runs po_match, with User2 showing interest 5, and User3 showing interest 4. Users schedules are NOT set.
        """
        matchesList = po_match(self.project)

        # Assert User2 is the first (Gave a interest of 5)
        self.assertTrue(matchesList[0][0] == self.user2)

        # Assert User3 is the second (Gave an interest of 4)
        self.assertTrue(matchesList[1][0] == self.user3)

        # Assert User2's score is greater than User3's
        self.assertTrue(matchesList[0][1][0] > matchesList[1][1][0])

    def testMatchWithProjectDesiringSkills(self):
        """
        Runs po_match, with the project desiring the skill User3 knows. Users schedules are NOT set.
        """
        # Add user3's skill as a desired skill
        self.project.desired_skills.add(self.skill2)

        matchesList = po_match(self.project)

        # Assert User3 is the first choice over User2
        self.assertTrue(matchesList[0][0] == self.user3)

        # Remove the project desired_skill we added
        self.project.desired_skills.remove(self.skill2)


    # TODO:
    def testMatchWithScheduleBonus(self):
        """
        Runs po_match, with user2's scheduling fitting into the existing member's schedule, and user3's not ligning up
        """

# TODO: sort
class SortMatchListTest(TestCase):
    """
    """
    def setUp(self):
        """
        Init any variables that are needed for testing
        """
        # create users
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'testing')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'testing')
        self.user3 = User.objects.create_user('user3', 'user3@test.com', 'testing')

        # create course
        self.course = Course.objects.create(name='TestCourse',slug='Test1', creator=self.user1)

    def tearDown(self):
        """
        Delete any variables that were created for testing
        """
        del self.user1
        del self.user2
        del self.user3

        del self.course

# TODO: auto_ros tests
class AutoSetRosterTest(TestCase):
    """
    """
    def setUp(self):
        """
        Init any variables that are needed for testing
        """
        # create users
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'testing')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'testing')
        self.user3 = User.objects.create_user('user3', 'user3@test.com', 'testing')

        # create course
        self.course = Course.objects.create(name='TestCourse',slug='Test1', creator=self.user1)

    def tearDown(self):
        """
        Delete any variables that were created for testing
        """
        del self.user1
        del self.user2
        del self.user3

        del self.course

    def testInitialTesting(self):
        auto = auto_ros(self.course)

# TODO: by_schedule tests
class GetAvailabilityScoreTest(TestCase):
    """
        Summary: Takes in a user and a project, compares users availability
            to the avalibility of other users in a specific project.
        Params: User - user object
                Project - Project object
        Returns: An integer that is floor(# meeting hours/ # pos meetings)
    """
    def setUp(self):
        """
        Init any variables that are needed for testing
        """

    def tearDown(self):
        """
        Delete any variables that were created for testing
        """

# TODO: adjust send_email to be more testable
class EmailTests(TestCase):
    def setUp(self):
        self.user1 = create_user("test1", "test1@test.com", "test1")
        self.recipient1 = create_user("recipient1", "recipient1@test.com", "recipient1")
        self.recipient2 = create_user("recipient2", "recipient2@test.com", "recipient2")

    def tearDown(self):
        del self.user1
        del self.recipient1
        del self.recipient2

    # TODO: adjust send_email to be more testable
    def test_norecipients_found(self):
        empty_list = []
        response = send_email(empty_list, "gtemail@test.com", "test_norecipients_found", "email content")
        self.assertTrue(response.content.decode("utf-8") == 'No recipients were found.')

    def test_single_recipient(self):
        response = send_email(self.recipient1, "gtemail@test.com", "test_single_recipient", "email content")
        self.assertTrue(response.content.decode("utf-8") == 'Email Sent!')

    def test_successful_recipientlist(self):
        recipient_list = []
        recipient_list.append(self.recipient1)
        recipient_list.append(self.recipient2)
        response = send_email(recipient_list, "gtemail@test.com", "test_single_recipient", "email content")
        self.assertTrue(response.content.decode("utf-8") == 'Email Sent!')

    def test_successful_emaillist(self):
        recipient_list = []
        recipient_list.append(self.recipient1.email)
        recipient_list.append(self.recipient2.email)
        response = send_email(recipient_list, "gtemail@test.com", "test_single_recipient", "email content")
        self.assertTrue(response.content.decode("utf-8") == 'Email Sent!')

    def test_bad_request(self):
        response = send_email(724, "gtemail@test.com", "test_bad_request", "email content")
        self.assertTrue(response.content.decode("utf-8") == 'Bad Request')

# TODO: parse csv tests
class ParseCsvTests(TestCase):

    def setUp(self):
        self.csv_path = settings.PROJECT_DIR
        pass

    def tearDown(self):
        pass

# TODO: search tests
class SearchTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

class CoreViewsTests(TestCase):
    def setUp(self):
        self.user1 = create_user("test1", "test1@test.com", "test1")
        self.client = Client()

    def tearDown(self):
        del self.client

    def test_view_about(self):
        response = self.client.get(reverse('about'))
        self.assertTrue(response.status_code == 200)

    def test_view_contact(self):
        response = self.client.get(reverse('contact'))
        self.assertTrue(response.status_code == 200)

    def test_view_landing(self):
        response = self.client.post('/')
        self.assertTrue(response.status_code == 200)

    def test_view_login_unauth(self):
        response = self.client.post('/login')
        self.assertTrue(response.status_code == 200)

    def test_view_login_auth(self):
        self.client.login(username='test1', password='test1')
        response = self.client.post('/login')        
        self.assertTrue(response.status_code == 200)
