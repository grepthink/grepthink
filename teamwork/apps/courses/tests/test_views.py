"""
test_views.py

Courses App View Tests
"""
from datetime import datetime, date, timedelta
from django.test import Client, TestCase
from django.contrib.auth.models import User
from teamwork.apps.courses.models import Course, Enrollment, Assignment, CourseUpdate
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

class UploadCsvViewTest(TestCase):
    """ Upload Csv View Tests """
    def setUp(self):
        # Create Test Prof
        self.prof1 = create_user("prof1", "prof1@test.com", "prof1")
        self.prof1.profile.isProf = True
        self.prof1.save()

        self.course = create_course("test course", "slugx", self.prof1)
        self.course.save()

        # Init Client
        self.client = Client()

        # Authenticate Professor
        self.client.login(username='prof1', password='prof1')

    def tearDown(self):
        del self.prof1
        del self.course
        del self.client

    def test_get_upload_csv_view(self):
        """ GET - upload_csv view """
        path = '/course/' + self.course.slug + '/upload_csv/'
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/upload_csv.html')

class ViewCourseTest(TestCase):
    """ View Course Test """
    def setUp(self):
        # Create Test Professor
        self.prof1 = create_user("prof1", "prof1@test.com", "prof1")
        self.prof1.profile.isProf = True
        self.prof1.save()

        # Create Test Course
        self.course = create_course("course1", "slug1", self.prof1)

        # Create Test User
        self.student = create_user("stud1", "stud1@test.com", "stud1")

        # Init Client
        self.client = Client()

    def tearDown(self):
        del self.prof1
        del self.course
        del self.client

    def test_get_view_as_student(self):
        """ GET - View One Course as a Student """
        # Enroll student in Course
        create_course_enrollment(self.student, self.course, 'student')

        # Authenticate Student
        self.client.login(username='stud1', password='stud1')

        # Get to /course/slug
        response = self.client.get('/course/' + self.course.slug + '/')

        # Assert Redirect to view the course
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/view_course.html')
        self.assertContains(response, 'course1')

    def test_post_view_as_student(self):
        """ POST - Posting to view_one_course acts as create a new Assignment """
        # Authenticate Prof
        self.client.login(username='prof1', password='prof1')

        # Post to /course/slug - acts as Creating a new Assignment
        data = {'due_date': date.today() + timedelta(days=7),
                'ass_date': date.today(),
                'ass_type': 'TODO',
                'ass_name': 'Test Assignment 1',
                'description': 'Assignment Description',
                'ass_number': 1}
        response = self.client.post('/course/' + self.course.slug + '/', data)

        # Assert after Assignment creation redirect to view_one_course occurred
        self.assertEqual(response.status_code, 302)

        # Assert a new Assignment object was created
        is_created = Assignment.objects.filter(ass_name='Test Assignment 1').exists()
        self.assertTrue(is_created)

class EditAssignmentTest(TestCase):
    """ Edit Assignment Test """
    def setUp(self):
        # Create Test Prof
        self.prof1 = create_user("prof1", "prof1@test.com", "prof1")
        self.prof1.profile.isProf = True
        self.prof1.save()

        self.course = create_course("test course", "slugx", self.prof1)
        self.course.save()

        # Create an Assignment that we will edit
        self.assignment = Assignment()
        self.assignment.ass_date = date.today()
        self.assignment.due_date = date.today() + timedelta(days=7)
        self.assignment.description = 'initial description'
        self.assignment.ass_type = 'Quiz'
        self.assignment.ass_name = 'Weekly Test Quiz'
        self.assignment.ass_number = 1
        self.assignment.save()

        # Add it to the Course's Assignments
        self.course.assignments.add(self.assignment)
        self.course.save()

        # Init Client
        self.client = Client()

        # Authenticate Professor
        self.client.login(username='prof1', password='prof1')

    def tearDown(self):
        del self.prof1
        del self.course
        del self.client

    def test_edit_assignment_not_enrolled(self):
        """ Tests rendering of edit_assignment view when not enrolled """
        # del self.enrollment
        response = self.client.get('/assignment/' + self.assignment.slug + '/edit/')

        # Assert view was rendered w/ edit_assignment template
        self.assertEqual(response.status_code, 302)
        # self.assertContains(response, 'You must be enrolled in the course to Edit Assignments', 302)

    def test_get_edit_assignment(self):
        """ Tests rendering of edit_assignment view """
        enrollment = create_course_enrollment(self.prof1, self.course, 'professor')
        enrollment.save()

        response = self.client.get('/assignment/' + self.assignment.slug + '/edit/')

        # Assert view was rendered w/ edit_assignment template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/edit_assignment.html')


    def test_edit_assignment(self):
        """ Tests Editing of edit_assignment view """
        enrollment = create_course_enrollment(self.prof1, self.course, 'professor')
        enrollment.save()

        data = {'due_date': date.today() + timedelta(days=7), 'ass_date': date.today(),
                'ass_type': self.assignment.ass_type, 'ass_name': self.assignment.ass_name,
                'description': 'after editing description', 'ass_number': self.assignment.ass_number}
        response = self.client.post('/assignment/' + self.assignment.slug + '/edit/', data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Assignment.objects.filter(description='after editing description').exists())

    def test_delete_assignment(self):
        """ Tests delete_assignment view method """
        enrollment = create_course_enrollment(self.prof1, self.course, 'professor')
        enrollment.save()

        slug = self.assignment.slug

        response = self.client.post('/assignment/' + slug + '/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(not Assignment.objects.filter(slug=slug).exists())

class CourseUpdateTest(TestCase):
    """ Tests regarding posting/deleting/editing Course Updates """
    def setUp(self):
        # Create Test Prof
        self.prof1 = create_user("prof1", "prof1@test.com", "prof1")
        self.prof1.profile.isProf = True
        self.prof1.save()

        # Create Course
        self.course = create_course("test course", "slugx", self.prof1)
        self.course.save()

        # Enroll Prof
        self.enrollment = create_course_enrollment(self.prof1, self.course, 'professor')
        self.enrollment.save()

        # Init Client
        self.client = Client()

        # Authenticate Professor
        self.client.login(username='prof1', password='prof1')

    def tearDown(self):
        del self.prof1
        del self.course
        del self.client

    def test_get_update_course(self):
        """ GET - /course/slug/update """
        response = self.client.get('/course/' + self.course.slug + '/update/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/update_course.html')

    def test_update_course(self):
        """ POST course update """
        data = {'title': 'Course Update Title', 'content':'This is a Course Update Test'}
        response = self.client.post('/course/' + self.course.slug + '/update/', data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(CourseUpdate.objects.filter(title=data['title']).exists())

    def test_get_edit_update(self):
        """ Tests GET to update_course_update """
        # Create Test Course Update
        data = {'title': 'Course Update Title', 'content':'This is a Course Update Test'}
        self.client.post('/course/' + self.course.slug + '/update/', data)
        created_update = CourseUpdate.objects.filter(title=data['title']).first()

        request_url = '/course/' + self.course.slug + '/update/' + str(created_update.id) + '/'
        response = self.client.get(request_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/update_course_update.html')

    def test_edit_course_update(self):
        """ Tests POST to update_course_update """
        # Create Test Course Update
        data = {'title': 'Course Update Title', 'content':'This is a Course Update Test'}
        self.client.post('/course/' + self.course.slug + '/update/', data)
        created_update = CourseUpdate.objects.filter(title=data['title']).first()

        data = {'title': created_update.title, 'content': 'Content Updated'}
        request_url = '/course/' + self.course.slug + '/update/' + str(created_update.id) + '/'
        response = self.client.post(request_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(CourseUpdate.objects.filter(content='Content Updated').exists())

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
