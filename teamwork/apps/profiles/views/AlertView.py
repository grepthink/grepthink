# Model Imports
from teamwork.apps.profiles.models import Profile, Alert
# Form Imports

# View Imports

# Other
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

@login_required
def view_alerts(request):

    user = request.user
    profile = Profile.objects.get(user=user)

    page_name = "Alerts"
    page_description = "Your notifications"

    unread = profile.unread_alerts()
    archive = profile.read_alerts()

    return render(request, 'profiles/alerts.html', {
        'profile': profile,
        'unread': unread,
        'archive': archive,
        'page_name': page_name,
        'page_description': page_description
        })

@login_required
def read_alert(request, ident):
    user = request.user
    alert = get_object_or_404(Alert, id=ident)
    if alert.to.id is user.id:
        alert.read = True
        alert.save()
    # else:
        # print("Attempt to read alert caught by internet police: " + str(alert.id))
    return redirect(view_alerts)

@login_required
def unread_alert(request, ident):
    user = request.user
    alert = get_object_or_404(Alert, id=ident)
    if alert.to.id is user.id:
        alert.read = False
        alert.save()
    return redirect(view_alerts)

@login_required
def archive_alerts(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    unread = profile.unread_alerts()

    for alert in unread:
        if alert.to.id is user.id:
            alert.read = True
            alert.save()

    return redirect(view_alerts)

@login_required
def delete_alert(request, ident):
    user = request.user
    alert = get_object_or_404(Alert, id=ident)
    if alert.to.id is user.id and alert.read is True:
        alert.delete()
    return redirect(view_alerts)
