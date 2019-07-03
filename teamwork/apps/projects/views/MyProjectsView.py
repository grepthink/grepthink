from django.core import serializers
from django.core.serializers import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from teamwork.apps.projects.models import Project
from django.shortcuts import get_list_or_404
from teamwork.apps.projects.forms import *
import json
import datetime


@login_required
def view_projects(request):
    """
    Public method that takes a request, retrieves all Project objects from the model,
    then calls _projects to render the request to template view_projects.html
    """
    active_projects = Project.get_my_active_projects(request.user)
    inactive_projects = Project.get_my_disabled_projects(request.user)

    return _projects(request, active_projects, inactive_projects)


def _projects(request, active, inactive):
    """
    Private method that will be used for paginator once I figure out how to get it working.
    """
    page = request.GET.get('page')

    # Populate with page name and title
    page_name = "My Projects"
    page_description = "Projects created by " + request.user.username
    title = "My Projects"
    return render(request, 'projects/view_projects.html', {'page_name': page_name,
                                                           'page_description': page_description, 'title': title,
                                                           'active': active, 'inactive': inactive})


def techs(request):
    return render(request, 'projects/view_projects.html', {})


@csrf_exempt
def saveProjectPlans(request, slug):
    projectPlans = ProjectPlan.objects.filter(project_id=slug);
    projectPlans.delete()
    plans = request.POST.get('plans')
    plansArr = json.loads(plans)
    for plan in plansArr:
        stories = plan.get("stories")
        for story in stories:
            tasks = story["tasks"]
            for task in tasks:
                print(task.get("finish_time"))
                if task.get("status") == 2 and task.get("finish_time") == "":
                    task["finish_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pp = ProjectPlan(content=json.dumps(plansArr, ensure_ascii=False), create_user_id=request.user.id, project_id=slug)
    pp.save()
    return JsonResponse({"code": 0, "msg": "success","data":plansArr})


def loadProjectPlans(request, slug):
    plans = ProjectPlan.objects.filter(project_id=slug)
    data = {}
    if plans:
        plansArr = json.loads(serializers.serialize("json", plans))
        data['plans'] = json.loads(plansArr[0].get("fields").get("content"))
    else:
        data['plans'] = []
    return JsonResponse(data)
