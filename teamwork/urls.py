"""teamwork URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from teamwork.apps.core import views as core_views
from teamwork.apps.courses import views as course_views
from teamwork.apps.profiles import views as profile_views
from teamwork.apps.projects import views as project_views

urlpatterns = [
        # CORE AND SIGNUP
        url(r'^$', core_views.index, name='index'),
        url(r'^about/$', core_views.about, name='about'),
        url(r'^signup/$', profile_views.signup, name='signup'),
        url(r'^search/$', core_views.search, name='search'),
        url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
        url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
        url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.password_reset_confirm, name='password_reset_confirm'),
        url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),

        # PROJECT
        # /create_project/
        url(r'^project/create/$', project_views.create_project, name='create_project'),
        # /view_projects/
        url(r'^project/all/', project_views.view_projects, name='view_projects'),
        # View individual project
        url(r'^project/(?P<slug>[^/]+)/$', project_views.view_one_project, name='view_one_project'),
        # Edit individual project (based on slug)
        url(r'^project/(?P<slug>[^/]+)/edit/$', project_views.edit_project, name='edit_project'),
        # Post update for individual project (based on slug)
        url(r'^project/(?P<slug>[^/]+)/update/$', project_views.post_update, name='post_update'),
        # Add new resource (based on slug)
        url(r'^project/(?P<slug>[^/]+)/resource/$', project_views.resource_update, name='resource_update'),
        # Update TSR information for normal tsr
        url(r'^project/(?P<slug>[^/]+)/tsr/$', project_views.tsr_update, name='tsr_update'),
        # View TSRs
        url(r'^project/(?P<slug>[^/]+)/view_tsr/$', project_views.view_tsr, name='view_tsr'),
        # View meeting times
        url(r'^project/(?P<slug>[^/]+)/meetings/$', project_views.view_meetings, name='view_meetings'),
        # Request to join Project
        url(r'^project/(?P<slug>[^/]+)/join/$', project_views.request_join_project, name='request_to_join'),
        # Add member to project
        url(r'^project/(?P<slug>[^/]+)/add/(?P<uname>[^/]+)$', project_views.add_member, name='add_member'),
        # Add member to project
        url(r'^project/(?P<slug>[^/]+)/reject/(?P<uname>[^/]+)$', project_views.reject_member, name='reject_member'),
        # Email Members of Project
        url(r'^project/(?P<slug>[^/]+)/email_members/$', project_views.email_project, name='email_project'),
        # select members (select2)
        url(r'^project/create/ajax/select_members/$', project_views.select_members, name='select_members'),
        url(r'^project/(?P<slug>[^/]+)/edit/ajax/edit_select_members/$', project_views.edit_select_members, name='edit_select_members'),
        url(r'^project/(?P<slug>[^/]+)/edit/ajax/add_desired_skills/$', project_views.add_desired_skills, name='add_desired_skills'),
        url(r'^project/create/ajax/add_desired_skills/$', project_views.create_desired_skills, name='create_desired_skills'),

        # COURSE
        #
        # View all courses
        url(r'^course/$', course_views.view_courses, name='view_course'),
        # Join a course (valid for all courses)
        url(r'^course/join/$', course_views.join_course, name='join_course'),
        # Create new course
        url(r'^course/new/$', course_views.create_course, name='create_course'),
        # View individual course (based on slug)
        url(r'^course/(?P<slug>[^/]+)/$', course_views.view_one_course, name='view_one_course'),
        # Delete individual course (based on slug)
        url(r'^course/(?P<slug>[^/]+)/delete/$', course_views.delete_course, name='delete_course'),
        # Edit individual course (based on slug)
        url(r'^course/(?P<slug>[^/]+)/edit/$', course_views.edit_course, name='edit_course'),
        # Stats page link
        url(r'^course/(?P<slug>[^/]+)/stats/$', course_views.view_stats, name='view_statistics'),
        # Email Roster link
        url(r'^course/(?P<slug>[^/]+)/email_roster/$', course_views.email_roster, name='email_roster'),
        # Email w/ CSV
        url(r'^course/(?P<slug>[^/]+)/email_csv/$', course_views.email_csv, name='email_csv'),
        # upload csv
        url(r'^course/(?P<slug>[^/]+)/upload_csv/$', course_views.upload_csv, name='upload_csv'),
        # Auto Generation page link
        url(r'^course/(?P<slug>[^/]+)/auto_gen/$', core_views.auto_gen, name='auto_gen'),
        # Setup link to assign students
        url(r'^course/(?P<slug>[^/]+)/auto_gen/assign/$',core_views.assign_auto, name='assign_auto'),
        # Post update to course (based on slug)
        url(r'^course/(?P<slug>[^/]+)/update/$', course_views.update_course, name='update_course'),
        # Edit existing update to course (based on slug and update id)
        url(r'^course/(?P<slug>[^/]+)/update/(?P<id>[^/]+)/$', course_views.update_course_update, name='update_course_update'),
        # Edit existing update to course (based on slug and update id)
        url(r'^course/(?P<slug>[^/]+)/update/(?P<id>[^/]+)/delete$',course_views.delete_course_update, name='delete_course_update'),
        # Button to lock interest
        url(r'^course/(?P<slug>[^/]+)/lock$',course_views.lock_interest, name='lock_interest'),
        # link to show interest page
        url(r'^course/(?P<slug>[^/]+)/show_interest/$',course_views.show_interest, name='show_interest'),
        # select2 for course
        url(r'^course/(?P<slug>[^/]+)/edit/ajax/edit_select_members/$', project_views.edit_select_members, name='edit_select_members'),
        # select2 for course
        # url(r'^course/(?P<slug>[^/]+)/claim/ajax/select_projects/$', course_views.select_projects, name='select_projects'),
        # Export Spreadsheet
        url(r'^course/(?P<slug>[^/]+)/export/$', course_views.export_xls, name='export_xls'),
        # Claim Projects (TA)
        url(r'^course/(?P<slug>[^/]+)/claim/$', course_views.claim_projects, name='claim_projects'),

        # ADMIN AND AUTH
        url(r'^admin/', admin.site.urls),
        url(r'^login', auth_views.login, {'template_name': 'core/login.html'}, name='login'),
        url(r'^logout', auth_views.logout, {'next_page': 'login'}, name='logout'),

        # PROFILE
        url(r'^user/(?P<username>[^/]+)/$', profile_views.view_profile, name='profile'),
        url(r'^user/(?P<username>[^/]+)/edit/$', profile_views.edit_profile, name='edit_profile'),
        url(r'^user/(?P<username>[^/]+)/edit_schedule/$', profile_views.edit_schedule, name='edit_schedule'),
        url(r'^user/(?P<username>[^/]+)/edit_schedule/ajax/save_event/$', profile_views.save_event, name='save_event'),
        url(r'^user/(?P<username>[^/]+)/edit/ajax/edit_skills/$', profile_views.edit_skills, name='edit_skills'),

        # MATCHES AND MATCHSTATS
        url(r'^matches/$', core_views.view_matches, name='view_matches'),
        # see why this user matches
        url(r'^matchstats/(?P<slug>[^/]+)/(?P<project_match_list>[^/]+)$', core_views.matchstats, name='matchstats'),

        # favicon
        url(r'^favicon.ico$', RedirectView.as_view(url='/static/images/favicon.ico',permanent=True),name="favicon"),

        # alerts
        url(r'^alerts/$', profile_views.view_alerts, name="view_alerts"),
        url(r'^alerts/(?P<ident>[^/]+)/read/$', profile_views.read_alert, name="read_alert"),
        url(r'^alerts/(?P<ident>[^/]+)/unread/$', profile_views.unread_alert, name="unread_alert"),
        url(r'^alerts/(?P<ident>[^/]+)/delete/$', profile_views.delete_alert, name="delete_alert"),
        url(r'^alerts/readall/$', profile_views.archive_alerts, name="archive_alerts"),

        ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
