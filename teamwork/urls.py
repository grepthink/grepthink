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
from django.contrib.auth import views as auth_views

from teamwork.apps.core import views as core_views
from teamwork.apps.profiles import views as profile_views
from teamwork.apps.projects import views as project_views

urlpatterns = [
    #/
    url(r'^$', core_views.home, name='home'),
    #/signup/
    url(r'^signup/$', profile_views.signup, name='signup'),
    #/create_project/
    url(r'create_project_SHIT', project_views.create_project, name='create_project'),
    #/view_projects/
    url(r'view_projects', project_views.view_projects, name='view_projects'),
    #/admin/
    url(r'^admin/', admin.site.urls),
    #login
    url(r'^login', auth_views.login, {'template_name': 'core/cover.html'},
        name='login'),
    #logout
    url(r'^logout', auth_views.logout, {'next_page': '/'}, name='logout'),
    #username/    
    #url(r'^(?P<username>[^/]+)/$', profile_views.profile, name='profile'),
    

    #just testing with this, will substitue for the version above
    url(r'^view_profile', profile_views.view_profile, name='view_profile')
]
