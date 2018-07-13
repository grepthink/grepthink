from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from teamwork.apps.projects.forms import TSR
from teamwork.apps.courses.models import Course, Assignment
from teamwork.apps.projects.models import Project, Tsr
from django.contrib.auth.models import User
from teamwork.apps.projects.views.ProjectView import view_one_project

from datetime import datetime

@login_required
def tsr_edit(request, slug, asg_slug):
    """
    Tsr Edit View

    - Queries for Tsr belonging to the Assignment(asg_slug) by the Evaluator(request.user)
    - Edits those Tsr's if the due date has not passed
    - Handles whether scrum_master or not by request param. TODO: reasearch another way to do this

    TODO: need to check if past due then don't allow an edit
    TODO: pass tsr.evaluator as prefix so we can display username also
    """
    page_name = "TSR Edit"
    page_description = "Edit TSR form"
    title = "TSR Edit"

    cur_proj = get_object_or_404(Project, slug=slug)
    asg = get_object_or_404(Assignment, slug=asg_slug)
    members = cur_proj.members.all()
    emails = [member.email for member in members]
    tsr_list = Tsr.objects.filter(ass_number=asg.ass_number, evaluator=request.user)

    scrum_master = False
    if "scrum_master" in str(request):
        scrum_master = True

    forms = []
    if request.method == 'POST':
        for tsr in tsr_list:
            form = TSR(request.POST, members=members,
                       emails=emails, prefix=tsr.evaluatee.email, scrum_master=scrum_master)

            if form.is_valid():
                # only editing these properties
                tsr.percent_contribution = form.cleaned_data.get('perc_contribution')
                tsr.positive_feedback = form.cleaned_data.get('pos_fb')
                tsr.negative_feedback = form.cleaned_data.get('neg_fb')
                tsr.tasks_completed = form.cleaned_data.get('tasks_comp')
                tsr.performance_assessment = form.cleaned_data.get('perf_assess')
                tsr.notes = form.cleaned_data.get('notes')
                tsr.save()

        return redirect(view_one_project, slug)

    else:
        # if request was not post then display forms
        for tsr in tsr_list:
            initial_dict = {'perc_contribution':tsr.percent_contribution,
                            'pos_fb':tsr.positive_feedback,
                            'neg_fb':tsr.negative_feedback,
                            'tasks_comp':tsr.tasks_completed,
                            'perf_assess':tsr.performance_assessment,
                            'notes':tsr.notes}
            form_i = TSR(initial=initial_dict, members=members,
                         emails=emails, prefix=tsr.evaluatee.email, scrum_master=scrum_master)
            forms.append(form_i)

    return render(request, 'projects/tsr_edit.html',{
        'forms':forms,'cur_proj': cur_proj, 'ass':asg,
        'page_name' : page_name, 'page_description': page_description,
        'title': title
    })
