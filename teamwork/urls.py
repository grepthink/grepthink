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
    url(r'^$', core_views.home, name='home'),
    url(r'^signup/$', profile_views.signup, name='signup'),
    url(r'create_project', project_views.create_project, name='create_project'),
    url(r'view_projects', project_views.view_projects, name='view_projects'),
    url(r'^admin/', admin.site.urls),
]
