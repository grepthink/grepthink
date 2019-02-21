from django.shortcuts import get_object_or_404, redirect, render

def contact(request):
    """
    Renders the ContactUs page
    """
    return render(request, 'core/contact.html')
