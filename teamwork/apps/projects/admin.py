# Django Modules
from django.contrib import admin

# Local Modules
from .models import Interest, Membership, Project, ProjectUpdate, ResourceUpdate, ProjectChat, Tsr, Analysis

# Register the following models for the admin site
admin.site.register(Project)
admin.site.register(Membership)
admin.site.register(ProjectUpdate)
admin.site.register(ResourceUpdate)
admin.site.register(Interest)
admin.site.register(ProjectChat)
admin.site.register(Tsr)
admin.site.register(Analysis)

