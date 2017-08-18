"""
Core views provide main site functionality.

"""
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from teamwork.apps.courses.models import *
from teamwork.apps.projects.models import *
from teamwork.apps.courses.views import *

from .forms import *
from .models import *
import re


def login_view(request):
    page_name = "Login"
    page_description = ""
    title = "Login"
    if request.user.is_authenticated():
        # TODO: get feed of project updates (or public projects) to display on login
        return render(request, 'courses/view_course.html', {'page_name': page_name,
            'page_description': page_description, 'title' : title})
    else:
        # Redirect user to login instead of public index (for ease of use)
        return render(request, 'core/login.html', {'page_name': page_name,
            'page_description': page_description, 'title' : title})

def index(request):
    """
    The main index of Teamwork, referred to as "Home" in the sidebar.
    Accessible to public and logged in users.
    """
    # TODO: get feed of project updates (or public projects) to display on login

    # Populate with defaults for not logged in user
    page_name = "GrepThink"
    page_description = "Build Better Teams"
    title = "Welcome"
    date_updates = None
    logged_in = request.user.is_authenticated();

    if not logged_in:
        return render(request, 'core/landing.html', {'page_name' : page_name,
            'page_description' : page_description, 'title' : title})

    # If the user is a professor, return the dashboard html
    if logged_in and request.user.profile.isProf:
        page_name = "Dashboard"
        page_description = "Instructor Control Panel"
        title = "Dashboard"
        all_courses = Course.get_my_created_courses(request.user)
        return render(request, 'core/dashboard.html', {'page_name' : page_name,
         'page_description' : page_description, 'title' : title,
         'all_courses' : all_courses})

    if logged_in:
        page_name = "Timeline"
        page_description = "Recent Updates from Courses and Projects"
        title = "Timeline"
        if (request.user.profile.isProf):
            all_courses = Course.get_my_created_courses(request.user)
        else:
            all_courses = Course.get_my_courses(request.user)
        date_updates = []
        for course in all_courses:
            course_updates = course.get_updates_by_date()
            date_updates.extend(course.get_updates_by_date())

    return render(request, 'core/index.html', {'page_name' : page_name,
         'page_description' : page_description, 'title' : title,
         'date_updates' : date_updates, 'logged_in' : logged_in})

def about(request):
    page_name = "Frequently Asked Questions"
    page_description = "GrepThink"
    title = "FAQ"
    return render(request, 'core/about.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title})

def search(request):
    """
    This works but...

    If a user enters multiple search terms seperated by space,
    only the last keyword will return results
    - andgates
    """

    page_name = "Search"
    page_description = "Results"
    title = "Search Results"

    context = {'page_name': page_name,
    'page_description': page_description, 'title' : title}

    if request.POST.get('q'):
        raw_keywords = request.POST.get('q')
        # print("Keywords:")
        # print(raw_keywords)

        keywords = []

        if raw_keywords is not None:
            if " " in raw_keywords:
                keywords = raw_keywords.split(" ")
            else:
                keywords.append(raw_keywords)
            for q in keywords:
                user_results = User.objects.filter(
                    Q( first_name__contains = q ) |
                    Q( last_name__contains = q ) |
                    Q( username__contains = q ) ).order_by('username')
                project_results = Project.objects.filter(
                    Q( title__contains = q ) |
                    Q( content__contains = q ) |
                    Q( tagline__contains = q ) ).order_by('title')
                course_results = Course.objects.filter(
                    Q( name__contains = q ) |
                    Q( info__contains = q ) ).order_by('name')

            if user_results:
                context['user_results'] = user_results
            if project_results:
                context['project_results'] = project_results
            if course_results:
                context['course_results'] = course_results

    return render(request, 'core/search_results.html', context)

@login_required
def view_matches(request):
    """
    Generic view for serving a list of projects and potential teammate matches for
        each project.
    """
    project_match_list = []
    course_set = []

    page_name = "View Matches"
    page_description = "View Matching Students"
    title = "View Matches"

    if request.user.profile.isProf:
        courses = Course.get_my_created_courses(request.user)
        for course in courses:
            for project in course.projects.all():
                p_match = po_match(project)
                project_match_list.extend([(course, project, p_match)])
            course_set.append(course)
    else:
        my_projects = Project.get_my_projects(request.user)
        my_created = Project.get_created_projects(request.user)
        projects = my_projects | my_created
        projects = list(set(projects))
        for project in projects:
            p_match = po_match(project)
            project_match_list.extend([(project, p_match)])


    return render(request, 'core/view_matches.html', {
        'project_match_list' : project_match_list, 'course_set': course_set, 'page_name': page_name,
            'page_description': page_description, 'title' : title})


def auto_gen(request, slug):
    """
    Generic view for serving a list of projects and potential teammate matches for
        each project.
    """
    page_name = "Potential Roster"
    page_description = "Auto Generate Groups"
    title = "Auto Generate Groups"

    course = get_object_or_404(Course, slug=slug)
    project_match_list = []

    auto = auto_ros(course)

    flag = False
    for i in auto:
        if i[1]:
            flag = True
            break

    # Get just the projects so partial_project_box.html can loop through easily.
    # Will have to changes this once we get a better ui for autogen.
    projects = [x[0] for x in auto]

    return render(request, 'core/auto_gen.html', {
        'auto_gen' : auto, 'course': course, 'projects':projects, 'page_name': page_name,
            'page_description': page_description, 'title' : title, 'flag': flag})

def assign_auto(request, slug):
    """
    Assign the students to auto-gen teams
    """
    course = get_object_or_404(Course, slug=slug)
    auto = auto_ros(course)

    for p in auto:
        for mem in p[1]:
            Membership.objects.create(user=mem, project=p[0], invite_reason='')

    return redirect(auto_gen, course.slug)





def matchstats(request, slug, project_match_list):
    """
        Displays why a user was matched with said project.
        Returns two dicts:
            -- skill_match:
                stores a user's skills that are similar with said projects'
                desired skills with their username as the key
            -- interest_match:
                Stores a users interest value and their reasoning for said project
                as a tuple with their username as the key

        TODO: could combine the two dicts if wanted.
    """

    # Page Information
    page_name = "Matchstats"
    page_description = "Stats on your matches"
    title = "Matchstats"

    matched_students = []
    skill_match = {}
    interest_match = {}

    cur_project = get_object_or_404(Project, slug=slug)
    cur_desiredSkills = cur_project.desired_skills.all()

    # match_list is a str object so parse it for usernames...
    # i'm sure theres a better way, couldn't pass the object
    regex = r"<User: [^>]*>"
    reg_match = re.finditer(regex, project_match_list)
    for item in reg_match:
        username = item.group().split(": ")[1].replace(">","")
        matched_students.append(username)

    # find each students' known_skills that are desired by cur_project
    for stud in matched_students:
        student = get_object_or_404(User, username=stud)
        profile = Profile.objects.get(user=student)
        similar_skills = []

        for k_skill in profile.known_skills.all():

            for d_skill in cur_desiredSkills:

                if (k_skill == d_skill):
                    similar_skills.append(k_skill)

        all_interests = cur_project.interest.all()
        interests = all_interests.filter(user=student)

        for interest in interests:
            interest_match[stud] = ([interest, interest.interest_reason])

        if (len(similar_skills) > 0):
            skill_match[stud] = similar_skills
        else:
            skill_match[stud] = ["No similar skills"]

    user = request.user

    return render(request, 'core/matchstats.html',{
        'page_name':page_name,'page_description':page_description,
        'title':title,'skill_match':skill_match, 'cur_project' : cur_project,
        'interest_match':interest_match
        })

@login_required
def tsr_update(request, slug):
    """
    public method that takes in a slug and generates a TSR
    form for user. Different form generated based on which
    button was pressed (scrum/normal)
    """
    user = request.user
    # current course
    cur_proj = get_object_or_404(Project, slug=slug)

    # get list of emails of users in current project
    member_num=len(cur_proj.members.all())
    members=list()
    emails=list()
    for i in range(member_num):
        members.append(cur_proj.members.all()[i])
        if(cur_proj.members.all()[i]!=user):
            emails.append(cur_proj.members.all()[i].email)
    course = Course.objects.get(projects=cur_proj)


    asgs = list(course.assignments.all())


    # if an assignment is not available, boolean is set to
    # false and user is redirected to project view when they
    # try to fill out a tsr
    asg_available = False
    if not asgs:
        print("No assignments")
    else:
        # if an assignment is available, the lines below will check the date
        # of the assignment, verify that todays date is in between the assigned
        # date and the due date, and set the boolean for true as well as making
        # the assignment number = the assignment number of the assignment object
        today = datetime.now().date()
        print(today)

        for asg in asgs:
            if "tsr" in asg.ass_type.lower():
                asg_ass_date = asg.ass_date
                asg_ass_date = datetime.strptime(asg_ass_date,"%Y-%m-%d").date()

                asg_due_date = asg.due_date
                asg_due_date = datetime.strptime(asg_due_date,"%Y-%m-%d").date()
                if asg_ass_date < today <= asg_due_date:
                    print("assignment in progress")
                    asg_available = True
                    asg_number = asg.ass_number


    # This checks if button clicked was scrum or non scrum
    params = str(request)
    if "scrum_master_form" in params:
        scrum_master = True
    else:
        scrum_master = False

    page_name = "TSR Update"
    page_description = "Update TSR form"
    title = "TSR Update"
    forms=list()

    if(asg_available):
        if request.method == 'POST':

            for email in emails:
                # grab form
                form = TSR(request.user.id, request.POST, members=members,
                    emails=emails,prefix=email, scrum_master=scrum_master)
                if form.is_valid():
                    # put form data in variables
                    data=form.cleaned_data
                    percent_contribution = data.get('perc_contribution')
                    positive_feedback = data.get('pos_fb')
                    negative_feedback = data.get('neg_fb')
                    tasks_completed = data.get('tasks_comp')
                    performance_assessment = data.get('perf_assess')
                    notes = data.get('notes')
                    evaluatee_query = User.objects.filter(email__iexact=email)
                    evaluatee = evaluatee_query.first()

                    # gets fields variables and saves them to project
                    cur_proj.tsr.add(Tsr.objects.create(evaluator=user,
                        evaluatee=evaluatee,
                        percent_contribution=percent_contribution,
                        positive_feedback=positive_feedback,
                        negative_feedback=negative_feedback,
                        tasks_completed=tasks_completed,
                        performance_assessment=performance_assessment,
                        notes=notes,
                        ass_number=int(asg_number)))

                    cur_proj.save()

            print(list(cur_proj.tsr.all()))
            return redirect(view_projects)

        else:
            # if request was not post then display forms
            for m in emails:
                form_i=TSR(request.user.id, request.POST, members=members,
                    emails=emails, prefix=m, scrum_master=scrum_master)
                forms.append(form_i)
            form = TSR(request.user.id, request.POST, members=members,
                emails=emails, scrum_master=scrum_master)
        return render(request, 'projects/tsr_update.html',
            {'forms':forms,'emails':emails,'cur_proj': cur_proj,
            'page_name' : page_name, 'page_description': page_description,
            'title': title})
    else:
        # need to change this redirect to display message
        # so that user is aware why they were redirected
        return redirect(view_projects)


@login_required
def view_tsr(request, slug):
    """
    public method that takes in a slug and generates a view for
    submitted TSRs
    """
    project = get_object_or_404(Project, slug=slug)
    tsrs = list(project.tsr.all())
    member_num=len(project.members.all())

    # put emails into list
    members=list()
    emails=list()
    for i in range(member_num):
        members.append(project.members.all()[i])
        emails.append(project.members.all()[i].email)

    # for every sprint, get the tsr's and calculate the average % contribution
    tsr_dicts=list()
    tsr_dict = list()
    sprint_numbers=Tsr.objects.values_list('ass_number',flat=True).distinct()
    for i in sprint_numbers.all():
        averages=list()
        tsr_dict=list()
        for member in members:
            tsr_single=list()
            # for every member in project, filter query using member.id
            # and assignment number
            for member_ in members:
                if member == member_:
                    continue
                tsr_query_result=Tsr.objects.filter(evaluatee_id=member.id).filter(evaluator_id=member_.id).filter(ass_number=i).all()
                if(len(tsr_query_result)==0):
                    continue
                tsr_single.append(tsr_query_result[len(tsr_query_result)-1])
            avg=0
            if(len(tsr_single)!=0):
                for tsr_obj in tsr_single:
                    avg=avg+tsr_obj.percent_contribution
                avg=avg/len(tsr_single)
            tsr_dict.append({'email':member.email, 'tsr' :tsr_single,
                'avg' : avg})
            averages.append({'email':member.email,'avg':avg})
        tsr_dicts.append({'number': i , 'dict':tsr_dict,
            'averages':averages})

    med = int(100/len(members))
    mid = {'low' : int(med*0.7), 'high' : int(med*1.4)}
    page_name = "Professor/TA TSR View"
    page_description = "View project TSR"
    title = "Professor/TA TSR View"

    if request.method == 'POST':

        return redirect(view_projects)
    return render(request, 'projects/view_tsr.html', {'page_name' : page_name, 'page_description': page_description, 'title': title, 'tsrs' : tsr_dicts, 'contribute_levels' : mid, 'avg':averages})
