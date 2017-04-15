# Template Style Guide
### Teamwork Project
#### Revision 1 | April 15, 2017

#### Goal: define a standard style for HTML templates in order to unify the Teamwork user interface.

## Structure of Templates:

All templates extend `base.html` which provides some commonly used "blocks".

## Page title and description:
The page tilte and description can be set dynamically in *views.py* like so:

'''python
def index(request):
    """
    The main index of Teamwork, reffered to as "Home" in the sidebar. 
    Accessible to public and logged in users.
    """

    # Populate with defaults for not logged in user
    page_name = "Explore"
    page_description = "Public Projects and Courses"

    if request.user.is_authenticated():
        # Set the logged in page name and description
        page_name = "Timeline"
        page_description = "Recent Updates from Courses and Projects"

    return render(request, 'core/index.html', {'page_name' : page_name,
         'page_description' : page_description})
'''
-- Taken from `core/views.py : index`