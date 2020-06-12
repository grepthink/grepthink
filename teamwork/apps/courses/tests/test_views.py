"""
test_views.py

Courses App View Tests
"""

from django.test import Client, TestCase
from django.contrib.auth.models import User
from teamwork.apps.courses.models import Course, Enrollment
from teamwork.apps.profiles.models import Alert

class BaseViewTest(TestCase):
    """
    Tests for the BaseView view
    """
    def setUp(self):
        # Create Test User
        self.user1 = create_user("stud1", "stud1@test.com", "stud1")

        # Create Test Prof
        self.prof1 = create_user("prof1", "prof1@test.com", "prof1")
        self.prof1.profile.isProf = True
        self.prof1.save()

        # Init Client
        self.client = Client()

    def tearDown(self):
        del self.client

    def test_student_create_course(self):
        """
        Only a User marked as Professor can create a course
        """
        self.client.login(username='stud1', password='stud1')
        response = self.client.post('/course/new/')

        # Check that user recieved the redirect response 302
        self.assertEqual(response.status_code, 302)

    def test_create_course(self):
        """
        Create Course Test
        """
        # Initial Course Count
        course_count = Course.objects.count()

        # Auth Prof
        self.client.login(username='prof1', password='prof1')
        
        # Post to /course/new/ with Course Data
        data = {'name': "test course",
                'info': "test course information",
                'term': "Fall"}
        response = self.client.post('/course/new/', data)

        # Assert redirect to upload csv occurred
        self.assertEqual(response.status_code, 302)

        # Assert a Course has been added
        self.assertEqual(Course.objects.count(), course_count + 1)

    def test_view_courses(self):
        """ View Courses Test """
        course1 = create_course("course1", "slug1", self.prof1)
        course2 = create_course("course2", "slug2", self.prof1)

        # student join both courses
        # Auth Student
        self.client.login(username='stud1', password='stud1')

        # Post to /course/join/
        data = {'code': course1.addCode}
        response1 = self.client.post('/course/join/', data)

        data = {'code': course2.addCode}
        response2 = self.client.post('/course/join/', data)

        response3 = self.client.get('/course/')
        self.assertEqual(response3.status_code, 200)
        self.assertContains(response3, "course1")
        self.assertContains(response3, "course2")

class JoinCourseTests(TestCase):
    """ Join Course Tests """
    def setUp(self):
        # Create Test User
        self.user1 = create_user("stud1", "stud1@test.com", "stud1")

        # Create Test Prof
        self.prof1 = create_user("prof1", "prof1@test.com", "prof1")
        self.prof1.profile.isProf = True
        self.prof1.save()

        # Create Course
        self.course = Course.objects.create(name='TestCourse', slug='Test1', creator=self.prof1)
        self.course.save()

        # Init Client
        self.client = Client()

    def tearDown(self):
        del self.client
        del self.user1
        del self.prof1

    def test_join_course(self):
        """ Join Course Test """
        # Student Prof
        self.client.login(username='stud1', password='stud1')

        # Initial Alert/Enrollment Count
        alert_count = Alert.objects.count()
        enrollment_count = Enrollment.objects.count()

        # Post to /course/join/
        data = {'code': self.course.addCode}
        response = self.client.post('/course/join/', data)

        # Ensure an Alert and Enrollment object were created
        self.assertEqual(Alert.objects.count(), alert_count + 1)
        self.assertEqual(Enrollment.objects.count(), enrollment_count + 1)

        # Assert Redirect to view the course
        self.assertEqual(response.status_code, 302)

class FileTests(TestCase):
    """ Upload/Export Data Tests """
    def test_upload_csv(self):
        """ Upload Csv Test """

    def test_export_xls(self):
        """ Export Xls Test """

# Helper Functions
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