# Required headers for sendgrid: (sendgrid, os)
import sendgrid
import os
from sendgrid.helpers.mail import *

from django.contrib.auth.models import User
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)

# csv
import csv
import codecs


"""
    Params: recipients -- QuerySet of students
            from_email -- The address that the email will come from (can be anything we want)
            subject    -- subject of the email
            content    -- content of the email

    IF Authorization error occurs its because:
        1. you dont have sendgrid.env file in root. Get from Discord (8/11)
        2. need to run 'source ./sendgrid.env'
"""
def send_email(recipients, gt_email, subject, content):

    student_email_list = []

    if type(recipients) is User:
        # only 1 member
        student_email_list.append(Email(recipients.email))
    elif type(recipients) is list:
        if type(recipients[0]) is str:
            for student in recipients:
                student_email_list.append(Email(student))
        else:
            # build list of emails of recipients
            for student in recipients:
                student_email_list.append(Email(student.email))
    else:
        print("bad response ", type(recipients))
        return HttpResponseBadRequest()

    # Handle email sending
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

    # TODO: not sure what to put here in the to_email as of now.  Don't really need this initial email to be added,
    # but I'm not sure how the Mail() constructor below works without it.
    # to_email = Email("initial_email@grepthink.com", "GrepThink")
    to_email = Email("mrp00pybutth0l3@yourmom.com", "GrepThink")

    from_email = Email(gt_email)

    # TODO: Content should be formatted in a professional way. I believe markup is/can be supported.
    final_content = Content("text/plain", content)
    mail = Mail(from_email, subject, to_email, final_content)

    # add multiple emails to the outgoing Mail object
    # creating Personalization instances makes it so everyone can't see everyone elses emails in the 'to:' of the email
    for email in student_email_list:
        p = Personalization()
        p.add_to(email)
        mail.add_personalization(p)

    # The following line was giving SSL Certificate errors.
    # Solution at: https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error/42334357#42334357
    response = sg.client.mail.send.post(request_body=mail.get())
    #
    # print(response.status_code)
    # print(response.body)
    # print(response.headers)


"""
    Not yet being used, attempted to use w/ Email attachments
"""
def handle_file(uploaded_file):

    with open(uploaded_file, 'wbr+') as f:
        print("Name:",f.name)

        if f.multiple_chunks(chunk_size=none):
            # then read chunk by chunk
            for chunk in uploaded_file.chunks():
                data.write(chunk)
        # else safe to read all at once
        else:
            data = f.read()


    encoded = base64.b64encode(data)
    return encoded


"""
parse csv file

return dict. Key (string) = FirstName, Lastname
             Value (string)= Email
"""
def parse_csv(csv_file):
    print(csv_file)
    data = {}

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
