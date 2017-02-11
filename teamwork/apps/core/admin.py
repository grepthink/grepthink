from django.contrib import admin

# Register your models here.

from .models import Course
from .models import Project
from .models import User

admin.site.register(Course)
admin.site.register(Project)
admin.site.register(User)
