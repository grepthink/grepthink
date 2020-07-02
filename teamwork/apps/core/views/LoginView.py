"""View for login page."""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from teamwork.apps.core.views import LandingView

from django.contrib.auth import views as auth_views

def login(request):
    """
    View for login page.

    Args:
        request (requests.request): Page request.

    Returns:
        django.shortcuts.render: Page render.
    """
    page_name = "Login"
    page_description = ""
    title = "Login"

    authenticated = request.user.is_authenticated()
    if authenticated:
        # If the user is a professor, render their dashboard
        if request.user.profile.isProf:
            return LandingView.render_dashboard(request)

        # Otherwise render timeline
        return LandingView.render_timeline(request)

    # if post attempt to authenticate the user
    if request.method == 'POST':
        return auth_views.login(request)

    # Redirect user to login instead of public index (for ease of use)
    return render(request, 'core/login.html', {
        'page_name': page_name,
        'page_description': page_description, 'title' : title
        })
