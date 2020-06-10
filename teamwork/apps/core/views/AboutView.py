"""Render 'about' page."""
from django.shortcuts import render


def about(request):
    """Render about page.

    Args:
        request (requests.request): Page request.

    Returns:
        django.shortcuts.render: Page render.
    """
    page_name = "Frequently Asked Questions"
    page_description = "GrepThink"
    title = "FAQ"
    return render(request, 'core/about.html', {'page_name': page_name,
                                               'page_description': page_description, 'title' : title})
