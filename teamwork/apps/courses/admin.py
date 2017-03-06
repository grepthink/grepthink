#import admin
from django.contrib import admin
#import course models
from .models import Course
#imports enrollment model
from .models import Enrollment

#registers the following models on the admin site
admin.site.register(Course)
admin.site.register(Enrollment)
