from django.contrib import admin

# Register your models here.

from .models import Project
from .models import Membership
from .models import ProjectUpdate


admin.site.register(Project)
admin.site.register(Membership)
admin.site.register(ProjectUpdate)
