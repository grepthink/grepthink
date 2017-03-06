# Django Modules
from django.contrib import admin

# Local Modules
from .models import Project
from .models import Membership
from .models import ProjectUpdate
from .models import Interest

# Register the following models for the admin site
admin.site.register(Project)
admin.site.register(Membership)
admin.site.register(ProjectUpdate)
admin.site.register(Interest)
