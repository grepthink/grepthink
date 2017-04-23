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
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from teamwork.apps.core import views as core_views
from teamwork.apps.profiles import views as profile_views
from teamwork.apps.projects import views as project_views
from teamwork.apps.courses import views as course_views

urlpatterns = [
        #/
        url(r'^$', core_views.index, name='index'),
        url(r'^about/$', core_views.about, name='about'),
        # /signup/
        url(r'^signup/$', profile_views.signup, name='signup'),
        # /create_project/
        url(r'^project/create/$', project_views.create_project, name='create_project'),
        # /view_projects/
        url(r'^project/all/', project_views.view_projects, name='view_projects'),
        # View individual project
        url(r'^project/(?P<slug>[^/]+)/$', project_views.view_one_project, name='view_one_project'),
        # Edit individual project (based on slug)
        url(r'^project/(?P<slug>[^/]+)/edit/$', project_views.edit_project, name='edit_project'),
        # Delete individual course (based on slug)
         url(r'^project/(?P<slug>[^/]+)/delete/$', project_views.delete_project, name='delete_project'),
        # Post update for individual project (based on slug)
        url(r'^project/(?P<slug>[^/]+)/update/$', project_views.post_update, name='post_update'),
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
        # Post update to course (based on slug)
        url(r'^course/(?P<slug>[^/]+)/update/$', course_views.update_course, name='update_course'),
        # Edit existing update to course (based on slug and update id)
        url(r'^course/(?P<slug>[^/]+)/update/(?P<id>[^/]+)/$', course_views.update_course_update, name='update_course_update'),
        # Edit existing update to course (based on slug and update id)
        url(r'^course/(?P<slug>[^/]+)/update/(?P<id>[^/]+)/delete$',course_views.delete_course_update, name='delete_course_update'),
        # /admin/
        url(r'^admin/', admin.site.urls),
        # /login/
        url(r'^login', auth_views.login, {'template_name': 'core/login.html'}, name='login'),
        #logout
        url(r'^logout', auth_views.logout, {'next_page': 'login'}, name='logout'),
        # /username/ - A users unique profile url
        url(r'^course/(?P<slug>[^/]+)/show_interest/$',course_views.show_interest, name='show_interest'),
        url(r'^user/(?P<username>[^/]+)/$', profile_views.view_profile, name='profile'),
        # /username/edit - Edit user profile
        url(r'^user/(?P<username>[^/]+)/edit/$', profile_views.edit_profile, name='edit_profile'),

        url(r'^user/(?P<username>[^/]+)/edit_schedule/$', profile_views.edit_schedule, name='edit_schedule'), 

        url(r'^user/(?P<username>[^/]+)/edit_schedule/ajax/save_event/$', profile_views.save_event, name='save_event'),

        url(r'^matches/$', core_views.view_matches, name='view_matches'),

        ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
