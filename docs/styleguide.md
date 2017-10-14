Template Style Guide
======
### Teamwork Project
#### Revision 1 | April 15, 2017

#### Goal: define a standard style for HTML templates in order to unify the Teamwork user interface.

## Structure of Templates:

All templates extend `base.html` which provides some commonly used "blocks".

## Page title and description:
The page tilte and description can be set dynamically in *views.py* like so:

```python
def index(request):
    """
    The main index of Teamwork, reffered to as "Home" in the sidebar. 
    Accessible to public and logged in users.
    """

    # Populate with defaults for not logged in user
    page_name = "Explore"
    page_description = "Public Projects and Courses"
    # Set the title of the tab
    title = "Explore"

    if request.user.is_authenticated():
        # Set the logged in page name and description
        page_name = "Timeline"
        page_description = "Recent Updates from Courses and Projects"
        title = "Timeline"

    return render(request, 'core/index.html', {'page_name' : page_name,
         'page_description' : page_description, 'title' : title})
```
*Taken from* `core/views.py : index`


Any that serves a page should first return page_name, page_description, and title.

See project views for examples of properly formated page info, specifically view_one_project.

**Please note that you may have to remove a hard coded title in the html.**

## Adding breadcrumbs to an HTML template.

Take a look at base.hmtl to see where the breadcrumb block is defined:
```
{% block breadcrumbs %}
    {# Breadcrumb implementation left to developers #}
    <ol class="breadcrumb">
      <li><a href="{% url 'index' %}">Home</a></li>
      {# Add your breadcrumbs in the crumb block #}
      {% block crumb %}
      {% endblock crumb %}
    </ol>
{% endblock breadcrumbs %}
```

In the HTML template that you would like to add breadcrumbs too, define a `crumb` block like so:
```
{# Add the breadcrumbs for this page #}
{% block crumb %}

{# Breadcrumb for the course that this project is in #}
<li><a href="{% url 'view_one_course' course.slug %}"> {{course.name}} </a></li>

{# Breadcrumb for this project #}
<li><a href="{% url 'view_one_project' project.slug %}"> {{project.title}} </a></li>

{% endblock crumb %}
```
Taken from view_project.html.

Note that the 'Home' breadcrumb will be prepopulated because it is defined in base.html.

## Nesting breadcrumbs

If you ever need to access the breadcrumbs from a page that you inherited from, you could do something like:
```
{% block crumb %}
{# Get the breadcrumbs from the page we inherited from #}
{{block.super}}

{# Breadcrumb I want to add to the end #}
<li><a href="{% url 'view_method' args %}"> Current Page Name </a></li>

{% endblock crumb %}
```
Using block.super basically just loads in whatever was in the block you inherited from.

I guess I should have used this instead of making the crumb block within the breadcrumb block but oh well.


## Unit Tests

Here's an example of testing a view:
```python
"""
"""
Teamwork: test_views.py

Unit tests for views.py in app projects.

Usuage: Run as a part of all test with `python manage.py test`
"""

from django.contrib.auth.models import UserManager
# Django Modules
from django.test import TestCase, override_settings
from django.urls import reverse

from teamwork.apps.profiles.models import *
from teamwork.apps.projects.models import *
from teamwork.apps.courses.models import *


def create_project(title, creator, tagline, content, slug, resource, avail_mem=True, sponsor=False):
    # Create a dummy project (with no M2M relationships) that will be associated with user1
    return Project.objects.create(title=title, creator=creator,
        tagline=tagline, content=content,
        avail_mem=avail_mem, sponsor=sponsor, slug=slug,resource=resource)

def create_user(username, email, password):
    # Create a test user as an attribute of ProjectTestCase, for future use
    #   (we're not testing user or profile methods here)
    return User.objects.create_user(username, email, password)

def create_course(name, slug, info, term):
    return Course.objects.create(name=name, slug=slug, info=info, term=term)


class ViewProjectTestCase(TestCase):
    """
    Tests the view_one_project method in projects/views.py

    References: 
    https://docs.djangoproject.com/en/1.11/topics/testing/overview/
    https://docs.djangoproject.com/en/1.11/intro/tutorial05/#testing-our-new-view
    https://docs.djangoproject.com/en/1.11/topics/testing/tools/#django.test.override_settings
    https://docs.djangoproject.com/en/1.11/ref/urlresolvers/#django.core.urlresolvers.reverse
    """
    def setUp(self):
        """
        Initialize project, user, and membership objects for use in test methods.

        # Actually not need in this simple test. But will be useful in other tests.
        # user1 = create_user('user_test1', 'test1@test.com', 'groupthink')
        # Membership.objects.create(user=user1, project=project1, invite_reason='')
        """

    @override_settings(STATICFILES_STORAGE = None)
    def test_view_one_project(self):
        """
        Confirms that view_one_project sucesfully returns a 200 response when given the
        slug of an existing project.

        Decorator override_settings to avoid errors with whitenoise when using client().
        """

        # The course is now looked up in view_one_project because it is needed for breadcrumbs.
        course1 = create_course("Test Course 1", "test-course1", "Test Info", "Test Term")

        # Create a test project to be servered
        project1 = create_project("Test Project 1", "user_test1", "Test Tagline 1", 
            "Test Content 1", "test1-slug", "Test Resource 1")

        # Add the project to the course many to many field so the course lookup is sucesfull.
        course1.projects.add(project1)

        # Get the response using reverse to load the url with keyword arg: slug of project 1
        response = self.client.get(reverse('view_one_project', kwargs={'slug':project1.slug}))

        # Confirm that view_one_project returned a response with status code 200 (page served sucesfully).
        self.assertEqual(response.status_code, 200)



```

**If we have a simple unit test that checks for a 200 status code, Travis will notify us whenever we accidentally break a part of the site**

**Less QA testing for everyone!**