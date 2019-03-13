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

    CAN OPTIONALLY INCLUDE A CONVERTER TYPE. I.e: <int: index>. Otherwise all <index> will be passed as string. -kp
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from teamwork.apps.core import helpers as core_helpers

# Project Imports
from teamwork.apps.projects.views import BaseView as ProjectBaseView
from teamwork.apps.projects.views import ProjectView, MyProjectsView, EditProjectView, TsrView, MeetingsView, EditTsrView

# Profile Imports
from teamwork.apps.profiles.views import BaseView as ProfileBaseView
from teamwork.apps.profiles.views import AlertView, EditProfileView, EditScheduleView, ProfileView,ViewSchedule
from teamwork.apps.profiles.views.EditScheduleView import import_schedule
# Course Imports
from teamwork.apps.courses.views import BaseView as CourseBaseView
from teamwork.apps.courses.views import CourseView, EditCourseView, EmailCourseView, InterestView, MyCoursesView, StatsView, MatchesView

# Core Imports
from teamwork.apps.core.views import AboutView, ContactView, LandingView, LoginView

urlpatterns = [
        # CORE AND SIGNUP
        url(r'^$', LandingView.index, name='index'),
        # Button to Disable course
        url(r'^(?P<slug>[^/]+)/disable/$',LandingView.disable , name='landing_disable'),
        # /about/
        url(r'^about/$', AboutView.about, name='about'),
        # /signup/
        url(r'^signup/$', ProfileBaseView.signup, name='signup'),
        # /contact/
        url(r'^contact/$', ContactView.contact, name='contact'),
        url(r'^profSignup/$', ProfileBaseView.profSignup, name='profSignup'),
        url(r'^search/$', core_helpers.search, name='search'),
        url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
        url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
        url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.password_reset_confirm, name='password_reset_confirm'),
        url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),

        # PROJECT
        # /create_project/
        url(r'^project/create/$', ProjectBaseView.create_project, name='create_project'),
        # /view_projects/
        url(r'^project/all/', MyProjectsView.view_projects, name='view_projects'),
        # View individual project
        url(r'^project/(?P<slug>[^/]+)/$', ProjectView.view_one_project, name='view_one_project'),
        # Edit individual project (based on slug)
        url(r'^project/(?P<slug>[^/]+)/edit/$', EditProjectView.edit_project, name='edit_project'),
        # Post update for individual project (based on slug)
        url(r'^project/(?P<slug>[^/]+)/update/$', ProjectView.post_update, name='post_update'),
        # Edit existing update to project (based on slug and update id)
        url(r'^project/(?P<slug>[^/]+)/update/(?P<id>[^/]+)/$', ProjectView.update_project_update, name='update_project_update'),
        # Delete existing update to project (based on slug and update id)
        url(r'^project/(?P<slug>[^/]+)/update/(?P<id>[^/]+)/delete$',ProjectView.delete_project_update, name='delete_project_update'),
        # Add new resource (based on slug)
        url(r'^project/(?P<slug>[^/]+)/resource/$', ProjectView.resource_update, name='resource_update'),
        # Edit existing resource to project (based on slug and resource id)
        url(r'^project/(?P<slug>[^/]+)/resource/(?P<id>[^/]+)/$', ProjectView.update_resource_update, name='update_resource_update'),
        # Delete existing resource to project (based on slug and resource id)
        url(r'^project/(?P<slug>[^/]+)/resource/(?P<id>[^/]+)/delete$',ProjectView.delete_resource_update, name='delete_resource_update'),
        # Create Scrum Master TSR
        url(r'^project/(?P<slug>[^/]+)/tsr/(?P<asg_slug>[^/]+)/smaster/$', TsrView.create_scrum_master_tsr, name='create_scrum_master_tsr'),
        # Update TSR information
        url(r'^project/(?P<slug>[^/]+)/tsr/(?P<asg_slug>[^/]+)/member/$', TsrView.create_member_tsr, name='create_member_tsr'),
        # Edit TSR information
        url(r'^project/(?P<slug>[^/]+)/tsr/(?P<asg_slug>[^/]+)/edit/$', EditTsrView.tsr_edit, name='tsr_edit'),
        # View TSRs
        url(r'^project/(?P<slug>[^/]+)/view_tsr/$', TsrView.view_tsr, name='view_tsr'),
        # View meeting times
        url(r'^project/(?P<slug>[^/]+)/meetings/$', MeetingsView.view_meetings, name='view_meetings'),
        # Request to join Project
        url(r'^project/(?P<slug>[^/]+)/join/$', ProjectView.request_join_project, name='request_to_join'),
        # Request to leave Project
        url(r'^project/(?P<slug>[^/]+)/leave/$', EditProjectView.leave_project, name='leave_project'),
        # Add member to project
        url(r'^project/(?P<slug>[^/]+)/add/(?P<uname>[^/]+)$', EditProjectView.add_member, name='add_member'),
        # Try add member to project
        url(r'^project/(?P<slug>[^/]+)/tryadd/(?P<uname>[^/]+)$', EditProjectView.try_add_member, name='try_add_member'),
        # Add member to project
        url(r'^project/(?P<slug>[^/]+)/reject/(?P<uname>[^/]+)$', ProjectView.reject_member, name='reject_member'),
        # Email Members of Project
        url(r'^project/(?P<slug>[^/]+)/email_members/$', ProjectBaseView.email_project, name='email_project'),
        # select members (select2)
        url(r'^project/create/ajax/select_members/$', core_helpers.select_members, name='select_members'),
        url(r'^project/(?P<slug>[^/]+)/edit/ajax/edit_select_members/$', core_helpers.edit_select_members, name='edit_select_members'),
        url(r'^project/(?P<slug>[^/]+)/edit/ajax/add_desired_skills/$', EditProjectView.add_desired_skills, name='add_desired_skills'),
        url(r'^project/(?P<slug>[^/]+)/edit/ajax/add_desired_techs/$', EditProjectView.add_desired_techs, name='add_desired_techs'),
        url(r'^project/create/ajax/add_desired_skills/$', EditProjectView.create_desired_skills, name='create_desired_skills'),
        url(r'^project/create/ajax/add_desired_techs/$', EditProjectView.create_desired_techs, name='create_desired_techs'),

        # COURSE
        # Delete individual assignment (based on slug)
        url(r'^assignment/(?P<slug>[^/]+)/delete/$', CourseView.delete_assignment, name='delete_assignment'),
        # Edit individual assignment (based on slug)
        url(r'^assignment/(?P<slug>[^/]+)/edit/$', CourseView.edit_assignment, name='edit_assignment'),

        # View all courses
        url(r'^course/$', CourseBaseView.view_courses, name='view_course'),
        # Join a course (valid for all courses)
        url(r'^course/join/$', CourseBaseView.join_course, name='join_course'),
        # Create new course
        url(r'^course/new/$', CourseBaseView.create_course, name='create_course'),
        # View individual course (based on slug)
        url(r'^course/(?P<slug>[^/]+)/$', CourseView.view_one_course, name='view_one_course'),
        # Delete individual course (based on slug)
        url(r'^course/(?P<slug>[^/]+)/delete_course/$', EditCourseView.delete_course, name='delete_course'),
        # Drop from a course based on a slug
        #url(r'^course/(?P<slug>[^/]+)/drop/$', course_views.drop_course, name='drop_course'),
        # Edit individual course (based on slug)
        url(r'^course/(?P<slug>[^/]+)/edit/$', EditCourseView.edit_course, name='edit_course'),
        # Stats page link
        url(r'^course/(?P<slug>[^/]+)/stats/$', StatsView.view_stats, name='view_statistics'),
        # Email Roster link
        url(r'^course/(?P<slug>[^/]+)/email_roster/$', EmailCourseView.email_roster, name='email_roster'),
        # Email w/ CSV
        url(r'^course/(?P<slug>[^/]+)/email_csv/$', EmailCourseView.email_csv, name='email_csv'),
        # upload csv
        url(r'^course/(?P<slug>[^/]+)/upload_csv/$', CourseBaseView.upload_csv, name='upload_csv'),
        # Auto Generation page link
        url(r'^course/(?P<slug>[^/]+)/auto_gen/$', MatchesView.auto_gen, name='auto_gen'),
        # Setup link to assign students
        url(r'^course/(?P<slug>[^/]+)/auto_gen/assign/$',MatchesView.assign_auto, name='assign_auto'),
        # Post update to course (based on slug)
        url(r'^course/(?P<slug>[^/]+)/update/$', CourseView.update_course, name='update_course'),
        # Edit existing update to course (based on slug and update id)
        url(r'^course/(?P<slug>[^/]+)/update/(?P<id>[^/]+)/$', CourseView.update_course_update, name='update_course_update'),
        # Edit existing update to course (based on slug and update id)
        url(r'^course/(?P<slug>[^/]+)/update/(?P<id>[^/]+)/delete$',CourseView.delete_course_update, name='delete_course_update'),
        # Button to lock interest
        url(r'^course/(?P<slug>[^/]+)/lock/$',EditCourseView.lock_interest, name='lock_interest'),
        # Button to Disable course
        url(r'^course/(?P<slug>[^/]+)/disable/$',EditCourseView.disable , name='disable'),
        # link to show interest page
        url(r'^course/(?P<slug>[^/]+)/show_interest/$',InterestView.show_interest, name='show_interest'),
        # select2 for course
        url(r'^course/(?P<slug>[^/]+)/edit/ajax/edit_select_members/$', core_helpers.edit_select_members, name='edit_select_members'),
        # select2 for course
        # url(r'^course/(?P<slug>[^/]+)/claim/ajax/select_projects/$', course_views.select_projects, name='select_projects'),
        # Export Spreadsheet
        url(r'^course/(?P<slug>[^/]+)/export/$', CourseBaseView.export_xls, name='export_xls'),
        # Export Interest
        url(r'^course/(?P<slug>[^/]+)/export_interest/$', InterestView.export_interest, name='export_interest'),
        # Claim Projects (TA)
        url(r'^course/(?P<slug>[^/]+)/claim/$', CourseView.claim_projects, name='claim_projects'),

        # ADMIN AND AUTH
        url(r'^admin/', admin.site.urls),
        url(r'^login', auth_views.login, {'template_name': 'core/login.html'}, name='login'),
        url(r'^logout', auth_views.logout, {'next_page': 'login'}, name='logout'),

        # PROFILE
        url(r'^user/(?P<username>[^/]+)/$', ProfileView.view_profile, name='profile'),
        url(r'^user/(?P<username>[^/]+)/view_schedule/$',ViewSchedule.load_schedule, name='view_schedule'),
        url(r'^user/(?P<username>[^/]+)/view_schedule/ajax/save_events/$', ViewSchedule.save_events, name='save_events'),
        url(r'^user/(?P<username>[^/]+)/edit/$', EditProfileView.edit_profile, name='edit_profile'),
        url(r'^user/(?P<username>[^/]+)/edit_schedule/$', EditScheduleView.edit_schedule, name='edit_schedule'),
        url(r'^user/(?P<username>[^/]+)/import_schedule$', EditScheduleView.import_schedule, name='import_schedule'),
        url(r'^user/(?P<username>[^/]+)/revoke_access$', EditScheduleView.revoke_access, name='revoke_access'),
        url(r'^user/(?P<username>[^/]+)/export_schedule$', EditScheduleView.export_schedule, name='export_schedule'),
        url(r'^user/(?P<username>[^/]+)/edit_schedule/ajax/save_event/$', EditScheduleView.save_event, name='save_event'),
        url(r'^user/(?P<username>[^/]+)/edit_schedule/ajax/save_time_limit/$', EditScheduleView.save_time_limit, name='save_time_limit'),
        url(r'^user/(?P<username>[^/]+)/edit/ajax/edit_skills/$', EditProfileView.edit_skills, name='edit_skills'),

        # For Refresh feature ( Refresh feature step 11 )
        url(r'^user/(?P<username>[^/]+)/edit_schedule/ajax/refresh_schedule/$', EditScheduleView.refresh_schedule, name='refresh_schedule'),
        url(r'^user/(?P<username>[^/]+)/view_schedule/ajax/refresh_schedule/$', ViewSchedule.refresh_schedule, name='refresh_schedules'),


        # MATCHES AND MATCHSTATS
        url(r'^matches/$', MatchesView.view_matches, name='view_matches'),
        # see why this user matches
        url(r'^matchstats/(?P<slug>[^/]+)/$', MatchesView.matchstats, name='matchstats'),

        # favicon
        url(r'^favicon.ico$', RedirectView.as_view(url='/static/images/favicon.ico',permanent=True),name="favicon"),

        # alerts
        url(r'^alerts/$', AlertView.view_alerts, name="view_alerts"),
        url(r'^alerts/(?P<ident>[^/]+)/read/$', AlertView.read_alert, name="read_alert"),
        url(r'^alerts/(?P<ident>[^/]+)/unread/$', AlertView.unread_alert, name="unread_alert"),
        url(r'^alerts/(?P<ident>[^/]+)/delete/$', AlertView.delete_alert, name="delete_alert"),
        url(r'^alerts/readall/$', AlertView.archive_alerts, name="archive_alerts"),

        ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#Django Toolbar Uncomment to turn on
#
# if settings.DEBUG:
#    import debug_toolbar
#    urlpatterns += [
#        url(r'^__debug__/', include(debug_toolbar.urls)),
#    ]
