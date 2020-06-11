"""Functional Tests for Core."""
import unittest

from selenium import webdriver


class NewVisitorTest(unittest.TestCase):
    """Test a New Visitor entering the site.

    Args:
        unittest (unittest.TestCase): A unit test.
    """
    def setUp(self):
        """Test setup."""
        self.browser = webdriver.Firefox()

    def tearDown(self):
        """Test teardown."""
        self.browser.quit()

    def test_can_load_page(self):
        """Ensures page can load."""
        self.browser.get('http://localhost:8000')
        self.assertIn('Teamwork | Teamwork', self.browser.title)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
