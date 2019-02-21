from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from teamwork.apps.projects.forms import TSR
from teamwork.apps.courses.models import Course, Assignment
from teamwork.apps.projects.models import Project, Tsr
from django.contrib.auth.models import User
from teamwork.apps.projects.views.ProjectView import view_one_project

from datetime import datetime

@login_required
def create_member_tsr(request, slug, asg_slug):
    """
    Method fires when the Scrum Master begins their Tsr Assignment
    """
    page_name = "Member TSR"

    title = "Member TSR"

    # Current Project
    cur_proj = get_object_or_404(Project, slug=slug)
    course = cur_proj.course.first()

    # Assignment object that the TSR's belong to
    asg = get_object_or_404(Assignment, slug=asg_slug)

    page_description = asg.ass_name

    # List of Members of the Current Project
    members = cur_proj.members.all()
    emails = [member.email for member in members]

    # Determine if the TSR is late
    late = asg.is_past_due

    if request.method == 'POST':
        # Create the TSR with the Form Data
        create_tsr_helper(request, members, emails, asg, cur_proj, False, late)

        return redirect(view_one_project, slug)
    else:
        # If request was not post then display forms
        # List of TSR Forms to be rendered
        forms = []

        # Display a TSR form for each email in the list
        for m in emails:
            form_i = TSR(request.POST, members=members,
                         emails=emails, prefix=m, scrum_master=False)

            # Add the TSR form to forms list
            forms.append(form_i)

    return render(request, 'projects/tsr_member.html',{
        'forms':forms,'cur_proj': cur_proj, 'ass':asg, 'course':course,
        'page_name' : page_name, 'page_description': page_description,
        'title': title
    })

@login_required
def create_scrum_master_tsr(request, slug, asg_slug):
    """
    Method fires when the Scrum Master begins their Tsr Assignment
    """
    page_name = "Scrum Master TSR"

    title = "Scrum Master TSR"

    cur_proj = get_object_or_404(Project, slug=slug)
    course = cur_proj.course.first()
    asg = get_object_or_404(Assignment, slug=asg_slug)
    today = datetime.now().date()
    members = cur_proj.members.all()
    emails = [member.email for member in members]

    page_description = asg.ass_name

    # Determine if the TSR is late
    late = asg.is_past_due

    forms = []
    if request.method == 'POST':
        # Create the TSR with the Form Data
        create_tsr_helper(request, members, emails, asg, cur_proj, True, late)

        return redirect(view_one_project, slug)
    else:
        # if request was not post then display forms
        for m in emails:
            form_i = TSR(request.POST, members=members,
                         emails=emails, prefix=m, scrum_master=True)
            forms.append(form_i)

    return render(request, 'projects/tsr_scrum_master.html',{
        'forms':forms,'cur_proj': cur_proj, 'ass':asg, 'course':course,
        'page_name' : page_name, 'page_description': page_description,
        'title': title
    })

def create_tsr_helper(request, members, email_list, assignment, project, scrum_master, late):
    """
    Creates a Tsr object, and fills its data with the form values
    """
    # For each email/member, create a Tsr
    for email in email_list:
        # grab form
        form = TSR(request.POST, members=members,
                   emails=email_list, prefix=email, scrum_master=scrum_master)
        if form.is_valid():
            tsr = Tsr()
            tsr.ass_number = assignment.ass_number
            tsr.percent_contribution = form.cleaned_data.get('perc_contribution')
            tsr.positive_feedback = form.cleaned_data.get('pos_fb')
            tsr.negative_feedback = form.cleaned_data.get('neg_fb')
            tsr.tasks_completed = form.cleaned_data.get('tasks_comp')
            tsr.performance_assessment = form.cleaned_data.get('perf_assess')
            tsr.notes = form.cleaned_data.get('notes')
            tsr.evaluator = request.user
            tsr.evaluatee =  User.objects.filter(email__iexact=email).first()
            tsr.late = late

            tsr.save()

            # gets fields variables and saves them to project
            project.tsr.add(tsr)
            project.save()
            assignment.subs.add(tsr)
            assignment.save()

@login_required
def view_tsr(request, slug):
    """
    public method that takes in a slug and generates a view for
    submitted TSRs
    """
    page_name = "View TSR"
    page_description = "Submissions"
    title = "View TSR"

    project = get_object_or_404(Project, slug=slug)
    tsrs = list(project.tsr.all())
    members = project.members.all()


    # put emails into list
    emails=list()
    for member in members:
        emails.append(member.email)

    # for every sprint, get the tsr's and calculate the average % contribution
    tsr_dicts=list()
    tsr_dict = list()
    sprint_numbers=Tsr.objects.values_list('ass_number',flat=True).distinct()
    for i in sprint_numbers.all():
        #averages=list()
        tsr_dict=list()
        for member in members:
            tsr_single=list()
            # for every member in project, filter query using member.id
            # and assignment number
            for member_ in members:
                if member == member_:
                    continue
                tsr_query_result=Tsr.objects.filter(evaluatee_id=member.id).filter(evaluator_id=member_.id).filter(ass_number=i).all()
                result_size = len(tsr_query_result)
                if(result_size == 0):
                    continue
                tsr_single.append(tsr_query_result[result_size - 1])

            avg=0

            if tsr_single:
                for tsr_obj in tsr_single:
                    # print("\n\n%d\n\n"%tsr_obj.percent_contribution)
                    avg = avg + tsr_obj.percent_contribution
                avg = avg / len(tsr_single)

            tsr_dict.append({'email':member.email, 'tsr' :tsr_single,'avg' : avg})
            averages.append({'email':member.email,'avg':avg})

        tsr_dicts.append({'number': i , 'dict':tsr_dict,
            'averages':averages})

    med = 1
    if len(members):
        med = int(100/len(members))

    mid = {'low' : int(med*0.7), 'high' : int(med*1.4)}


    if request.method == 'POST':
        return redirect(view_projects)
    return render(request, 'projects/view_tsr.html', {'page_name' : page_name, 'page_description': page_description, 'title': title, 'tsrs' : tsr_dicts, 'contribute_levels' : mid, 'avg':averages})
