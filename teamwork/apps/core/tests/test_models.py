"""
Core App Model Tests
"""
from django.contrib.auth.models import User
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from teamwork.apps.core.models import EmailAddressAuthBackend, po_match, sort, auto_ros, by_schedule
from teamwork.apps.core.helpers import send_email
from teamwork.apps.courses.models import Course, Enrollment
from teamwork.apps.projects.models import Interest, Project
from teamwork.apps.profiles.models import Skills

class AuthenticateWithEmailTest(TestCase):
    """Creates a user and asserts return values are correct from authenticate method."""
    def setUp(self):
        """Init any variables that are needed for testing."""
        self.user1 = User.objects.create_user('user_test1', 'test1@test.com', 'groupthink')

    def tearDown(self):
        """Delete any variables that were created for testing."""
        del self.user1

    def test_authenticate_success(self):
        """ Attempt to authenticate user w/ correct email address and pw and assert user object is returned """
        user = EmailAddressAuthBackend.authenticate(self, username='test1@test.com', password='groupthink')
        self.assertTrue(isinstance(user, User))

    def test_authenticate_fail(self):
        """Attempt to authenticate user w/ incorrect password and assert user object is None."""
        user = EmailAddressAuthBackend.authenticate(self, username='test1@test.com', password='incorrect')
        self.assertIsNone(user)

class FindProjectMatchesTest(TestCase):
    """Tests for the po_match method."""
    def setUp(self):
        """Init any variables that are needed for testing."""
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
        """Delete any variables that were created for testing."""
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

    def test_match_without_schedule_bonus(self):
        """
        Runs po_match, with User2 showing interest 5, and User3 showing interest 4.

        Users schedules are NOT set.
        """
        matchesList = po_match(self.project)

        # Assert User2 is the first (Gave a interest of 5)
        self.assertTrue(matchesList[0][0] == self.user2)

        # Assert User3 is the second (Gave an interest of 4)
        self.assertTrue(matchesList[1][0] == self.user3)

        # Assert User2's score is greater than User3's
        self.assertTrue(matchesList[0][1][0] > matchesList[1][1][0])

    def test_match_with_project_desiring_skills(self):
        """
        Runs po_match, with the project desiring the skill User3 knows.

        Users schedules are NOT set.
        """
        # Add user3's skill as a desired skill
        self.project.desired_skills.add(self.skill2)

        matchesList = po_match(self.project)

        # Assert User3 is the first choice over User2
        self.assertTrue(matchesList[0][0] == self.user3)

        # Remove the project desired_skill we added
        self.project.desired_skills.remove(self.skill2)
    
    def test_match_with_schedule_bonus(self):
        """Runs po_match, with user2's scheduling fitting into the existing member's schedule, and
        user3's not ligning up. TODO"""

    def testMatchWithScheduleBonus(self):
        """ TODO """        

class SortMatchListTest(TestCase):
    """ TODO: Create this test """

    def setUp(self):
        """Init any variables that are needed for testing."""
        # create users
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'testing')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'testing')
        self.user3 = User.objects.create_user('user3', 'user3@test.com', 'testing')

        # create course
        self.course = Course.objects.create(name='TestCourse',slug='Test1', creator=self.user1)

    def tearDown(self):
        """Delete any variables that were created for testing."""
        del self.user1
        del self.user2
        del self.user3

        del self.course

class AutoSetRosterTest(TestCase):
    """ TODO: Create this test """

    def setUp(self):
        """Init any variables that are needed for testing."""
        # create users
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'testing')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'testing')
        self.user3 = User.objects.create_user('user3', 'user3@test.com', 'testing')

        # create course
        self.course = Course.objects.create(name='TestCourse',slug='Test1', creator=self.user1)

    def tearDown(self):
        """Delete any variables that were created for testing."""
        del self.user1
        del self.user2
        del self.user3

        del self.course

    def test_auto_ros(self):
      """ TODO """
      auto = auto_ros(self.course)

class GetAvailabilityScoreTest(TestCase):
    """
        Tests models.by_schedule()

        TODO: Create this test
    """
    def setUp(self):
        """Init any variables that are needed for testing."""

    def tearDown(self):
        """Delete any variables that were created for testing."""

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

def create_user(username, email, password):
    """
    Create a User helper

    Args:
        username: (str) Username of the new user
        email: (str) Email of the new user
        password: (str) Password of the new user
    """    
    return User.objects.create_user(username, email, password)