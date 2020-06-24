from django.contrib.auth.models import User
from django.test import TestCase
from teamwork.apps.profiles.forms import SignUpForm
from teamwork.apps.profiles.views.BaseView import find_available_username


# Create your tests here.
class DuplicateSignUpTest(TestCase):
    """Creates a user and asserts return values are correct from authenticate method."""
    def setUp(self):
        """Init any variables that are needed for testing."""
        self.user1 = User.objects.create_user('test', 'test@testing.com', 'pw')

    def tearDown(self):
        """Delete any variables that were created for testing."""
        del self.user1

    def test_next_available_username(self):
        """Attempt to authenticate user w/ correct email address and pw and assert user object is
        returned."""
        # Find the next available username
        next_username = find_available_username("test")

        # assert it is test1
        self.assertTrue(next_username == "test1")

        # create that user w/ username test1
        self.user2 = User.objects.create_user('test1', 'test@another.com', 'pw')

        # next iteration should find that the next avail username is test2
        next_username = find_available_username("test")

        # assert it is test2
        self.assertTrue(next_username == "test2")

class SignupValidationTest(TestCase):
    """Test Signup Validation."""
    def test_reserved_word_raises_error(self):
        """Assure that using a reserved word raises ValidationError."""
        entered_email = "admin@testing.com"
        pw = "passwordtest"
        sign_up_form = SignUpForm(data={'email': entered_email, 'password':pw, 'confirm_password': pw})
        self.assertFalse(sign_up_form.is_valid())

    def test_successful_entry(self):
        """Assure that using a valid email address doesn't raise ValidationError."""
        entered_email = "kp123@testing.com"
        pw = "passwordtest"
        sign_up_form = SignUpForm(data={'email': entered_email, 'password': pw, 'confirm_password': pw})
        self.assertTrue(sign_up_form.is_valid())
