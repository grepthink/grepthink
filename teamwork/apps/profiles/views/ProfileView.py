# Django Imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User

# Model Imports
from teamwork.apps.profiles.models import Profile
from teamwork.apps.projects.models import Project
from teamwork.apps.courses.models import Course

# Form Imports
from teamwork.apps.profiles.forms import *

# View Imports

@login_required
def view_profile(request, username):
    """
    Public method that takes a request and a username.  Gets an entered 'skill' from the form
    and stores it in lowercase if it doesn't exist already. Renders profiles/profile.html.

    """

    page_user = get_object_or_404(User.objects.prefetch_related('profile'), username=username)
    user = request.user
    projects = Project.get_my_projects(page_user)
    profile = Profile.objects.get(user=user)
    courses = Course.get_my_courses(page_user)
    page_name = "Profile"
    page_description = "%s's Profile"%(page_user.username)
    title = "View Profile"

    # # gets all interest objects of the current user
    # my_interests = Interest.objects.filter(user=user)
    # # gets all projects where user has interest
    # my_projects = Project.objects.filter(interest__in=my_interests)

    return render(request, 'profiles/profile.html', {
        'page_user': page_user, 'profile':profile, 'page_name' : page_name, 'page_description': page_description, 'title': title,
        'projects': projects, 'courses': courses})
