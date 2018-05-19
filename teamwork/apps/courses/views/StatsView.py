# StatsView
from django.contrib.auth.decorators import login_required
from teamwork.apps.courses.models import Course, Enrollment
from teamwork.apps.projects.models import Membership
from django.shortcuts import get_object_or_404, redirect, render
from teamwork.apps.courses.views.CourseView import view_one_course

@login_required
def view_stats(request, slug):
    cur_course = get_object_or_404(Course.objects.prefetch_related('creator', 'projects', 'projects__members'), slug=slug)
    page_name = "Statistics"
    page_description = "Statistics for %s"%(cur_course.name)
    title = "Statistics"
    enrollment = Enrollment.objects.filter(user=request.user, course=cur_course)

    if not request.user.profile.isGT:
        if enrollment.count():
            user_role = enrollment.first().role
        else:
            user_role = "not enrolled"
    else:
        user_role = 'GT'

    if request.user.profile.isGT:
        pass
    elif not request.user==cur_course.creator:
        if not user_role=="ta":
            return redirect(view_one_course, cur_course.slug)

    students_num = Enrollment.objects.filter(course = cur_course, role="student")

    staff = cur_course.get_staff()
    staff_ids=[o.id for o in staff]

    students_projects = []
    students_projects_not = []
    emails = []
    cleanup_projects = []

    taken=list(Membership.objects.prefetch_related('user').values_list('user', flat=True).filter(project__in=cur_course.projects.all()))

    temp_in=cur_course.students.filter(id__in=taken+staff_ids).order_by('username')
    num_in = temp_in.count()
    students_projects=list(temp_in)

    temp_out=cur_course.students.exclude(id__in=taken+staff_ids).order_by('username')
    num_not = temp_out.count()
    students_projects_not=list(temp_out)

    num_total = num_in+num_not

    temp_proj=cur_course.projects.all().extra(\
    select={'lower_title':'lower(title)'}).order_by('lower_title').prefetch_related('members')
    num_projects = temp_proj.count()
    cleanup_projects=list(temp_proj)

    emails=list(cur_course.students.values_list('email', flat=True).order_by('email').exclude(id__in=staff_ids))

    return render(request, 'courses/view_statistics.html', {
        'cur_course': cur_course, 'cleanup_projects': cleanup_projects,'num_projects': num_projects,
        'students_projects': students_projects, 'students_projects_not': students_projects_not,
        'emails': emails, 'page_name' : page_name, 'page_description': page_description,
        'title': title, 'num_in': num_in, 'num_not': num_not, 'num_total': num_total
        })
