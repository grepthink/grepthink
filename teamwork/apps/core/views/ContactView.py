"""Render 'Contact Us' Page."""
from django.shortcuts import render


def contact(request):
    """Render Contact Us page.

    Args:
        request (requests.request): Page request.

    Returns:
        django.shortcuts.render: Page render.
    """
    return render(request, 'core/contact.html')
