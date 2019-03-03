# Django Modules
from django.contrib import admin

# Local Modules
from .models import Interest, Membership, Project, ProjectUpdate, ResourceUpdate, ProjectChat, Tsr, Techs

# Register the following models for the admin site
admin.site.register(Project)

# admin.site.unregister(Techs)
admin.site.register(Techs)

admin.site.register(Membership)
admin.site.register(ProjectUpdate)
admin.site.register(ResourceUpdate)
admin.site.register(Interest)
admin.site.register(ProjectChat)
admin.site.register(Tsr)
