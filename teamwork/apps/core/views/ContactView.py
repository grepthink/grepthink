from django.shortcuts import render


def contact(request):
    """
    Renders the ContactUs page
    """
    return render(request, 'core/contact.html')
