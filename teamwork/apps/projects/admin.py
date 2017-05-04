# Django Modules
from django.contrib import admin

# Local Modules
from .models import Interest, Membership, Project, ProjectUpdate

# Register the following models for the admin site
admin.site.register(Project)
admin.site.register(Membership)
admin.site.register(ProjectUpdate)
admin.site.register(Interest)
