from django.contrib import admin

# Register your models here.

from .models import Course
from .models import Enrollment

admin.site.register(Course)
admin.site.register(Enrollment)

