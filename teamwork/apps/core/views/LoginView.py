from django.shortcuts import render


def login_view(request):
    page_name = "Login"
    page_description = ""
    title = "Login"
    if request.user.is_authenticated():
        # TODO: get feed of project updates (or public projects) to display on login
        return render(request, 'courses/view_course.html', {
            'page_name': page_name,
            'page_description': page_description, 'title': title
        })
    else:
        # Redirect user to login instead of public index (for ease of use)
        return render(request, 'core/login.html', {
            'page_name': page_name,
            'page_description': page_description, 'title': title
        })
