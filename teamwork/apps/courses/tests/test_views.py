"""
test_views.py

Courses App View Tests
"""

from django.test import Client, TestCase
from django.contrib.auth.models import User
from teamwork.apps.courses.models import Course

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

    def test_join_course(self):
        """ Join Course Test """

    def test_upload_csv(self):
        """ Upload Csv Test """

    def test_export_xls(self):
        """ Export Xls Test """    

def create_user(username, email, password):
    """
    Create a User helper

    Args:
        username: (str) Username of the new user
        email: (str) Email of the new user
        password: (str) Password of the new user
    """    
    return User.objects.create_user(username, email, password)
