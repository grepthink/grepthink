"""Helper functions for core module."""
# csv
import csv

from django.conf import settings
from django.contrib.auth.decorators import login_required
# Django
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect, JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Email, Mail, Personalization
from teamwork.apps.courses.models import Course
from teamwork.apps.projects.models import Project


def send_email(recipients, gt_email, subject, content):
    """Sends email.
    If an authorization error occurs ensure endgrid.env file is in root, then 'source ./sendgrid.env'

    Args:
        recipients (User or list): Individual User or list of students.
        gt_email (str): The address that the email will come from (can be anything we want).
        subject (str): subject of the email.
        content (str): content of the email.

    Returns:
        HttpResponse: HttpResponse.
    """

    # Check if the recipients list is empty
    if not recipients:
        return HttpResponse("No recipients were found.")

    student_email_list = []

    # Only a single student
    if isinstance(recipients, User):
        student_email_list.append(Email(recipients.email))

    elif isinstance(recipients, list):
        if isinstance(recipients[0], str):
            for student in recipients:
                student_email_list.append(Email(student))
        else:
            for student in recipients:
                student_email_list.append(Email(student.email))
    else:
        return HttpResponseBadRequest("Bad Request")

    # Handle email sending
    sendgrid = SendGridAPIClient(settings.EMAIL_SENDGRID_KEY)

    mail = Mail()
    mail.from_email = Email(gt_email)
    mail.subject = subject
    mail.add_content(Content("text/plain", content))

    if settings.DEBUG:
        # if debug, send email to grepthink email
        personalization = Personalization()
        # If you wish to receive emails to personal email you can refector the below email. Do NOT update repo.
        personalization.add_to(Email("testing@grepthink.com"))
        mail.add_personalization(personalization)
    else:
        # add recipients to the outgoing Mail object
        # Ensure everyone can't see everyone elses emails in the 'to:' of the email
        for email in student_email_list:
            personalization = Personalization()
            personalization.add_to(email)
            mail.add_personalization(personalization)

    sendgrid.client.mail.send.post(request_body=mail.get())

    return HttpResponse("Email Sent!")

def parse_csv(csv_file):
    """Parse a CSV File.

    Args:
        csv_file (file.file): CSV File containing firstname, last name, and email.

    Returns:
        dict(str): Dictionary of name: email.
    """

    data = dict()
    contents = csv_file.read().decode("utf-8")

    # split contents of csv on new line, iterable is needed for csv.reader
    lines = contents.splitlines()

    # does all the backend splitting of csv, from 'csv' module
    reader = csv.reader(lines)
    header = ""

    # search first line for keywords
    for line in reader:
        header = line
        break

    firstNameIndex = -1
    lastNameIndex = -1
    emailIndex = -1
    i = 0

    for column in header:
        search = column.lower()
        if not search.find("name") == -1:
            # found name in column
            if not search.find("first") == -1:
                # found first name
                firstNameIndex = i
            if not search.find("last") == -1:
                # found last name
                lastNameIndex = i
        elif not search.find("email") == -1:
            # found email in column
            emailIndex = i
        i = i + 1

    for row in reader:
        fullname = row[firstNameIndex] + row[lastNameIndex]
        email = row[emailIndex]
        # Save student in dict, key=fullname & value=email
        data[fullname] = email

    return data

def select_members(request):
    """Select members in a form.

    Args:
        request (requests.request): Page request.

    Returns:
        HttpResponse: HttpResponse.
    """
    if request.method == 'POST' and request.is_ajax():
        return HttpResponse("Form Submitted")

    if request.method == 'GET' and request.is_ajax():
        # JSON prefers dictionaries over lists.
        data = dict()
        # A list in a dictionary, accessed in select2 ajax
        data['items'] = []
        query = request.GET.get('q')
        if query is not None:
            results = User.objects.filter(
                Q(first_name__contains=query)|
                Q(last_name__contains=query)|
                Q(username__contains=query)).order_by('username')
        for user in results:
            data['items'].append({'id': user.username, 'text': user.username})
        return JsonResponse(data)

    return HttpResponse("Failure")

#pylint:disable=unused-argument
def edit_select_members(request, slug):
    """Edit selected members.

    Args:
        request (requests.request): Page request.
        slug (str): A short label for something, containing only letters, numbers, underscores or hyphens.

    Returns:
        HttpResponse: HttpResponse.
    """
    if request.method == 'POST' and request.is_ajax():
        return HttpResponse("Form Submitted")

    elif request.method == 'GET' and request.is_ajax():
        # JSON prefers dictionaries over lists.
        data = dict()
        # A list in a dictionary, accessed in select2 ajax
        data['items'] = []
        query = request.GET.get('q')
        if query is not None:
            results = User.objects.filter(
                Q(first_name__contains=query)|
                Q(last_name__contains=query)|
                Q(username__contains=query)).order_by('username')
        for user in results:
            data['items'].append({'id': user.username, 'text': user.username})
        return JsonResponse(data)

    return HttpResponse("Failure")


@login_required
def search(request):
    """Search function.
    NOTE: If a user enters multiple search terms seperated by space,
    only the last keyword will return results

    Args:
        request (requests.request): Page request.

    Returns:
        django.shortcuts.render: Page render.
    """
    page_name = "Search"
    page_description = "Results"
    title = "Search Results"

    context = {'page_name': page_name,
               'page_description': page_description, 'title' : title}

    if request.POST.get('q'):
        raw_keywords = request.POST.get('q')
        keywords = []

        if raw_keywords is not None:
            if " " in raw_keywords:
                keywords = raw_keywords.split(" ")
            else:
                keywords.append(raw_keywords)
            for query in keywords:
                user_results = User.objects.filter(
                    Q(first_name__contains=query) |
                    Q(last_name__contains=query) |
                    Q(username__contains=query)).order_by('username')
                project_results = Project.objects.filter(
                    Q(title__contains=query) |
                    Q(content__contains=query ) |
                    Q(tagline__contains=query ) ).order_by('title')
                # NOTE: Course has no member 'objects'
                course_results = Course.objects.filter(
                    Q(name__contains=query )|
                    Q(info__contains=query)).order_by('name')

            if user_results:
                context['user_results'] = user_results
            if project_results:
                context['project_results'] = project_results
            if course_results:
                context['course_results'] = course_results

    return render(request, 'core/search_results.html', context)
