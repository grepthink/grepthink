#from django.test import TestCase

# Create your tests here.


import unittest

from selenium import webdriver


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_load_page(self):
        self.browser.get('http://localhost:8000')
        self.assertIn('Teamwork | Teamwork', self.browser.title)
        

if __name__ == '__main__':
    unittest.main(warnings='ignore')
