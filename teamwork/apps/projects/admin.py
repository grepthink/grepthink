# Django Modules
from django.contrib import admin

# Local Modules
from .models import (Interest, Membership, Project, ProjectChat, ProjectUpdate,
                     ResourceUpdate, Tsr)

# Register the following models for the admin site
admin.site.register(Project)
admin.site.register(Membership)
admin.site.register(ProjectUpdate)
admin.site.register(ResourceUpdate)
admin.site.register(Interest)
admin.site.register(ProjectChat)
admin.site.register(Tsr)
