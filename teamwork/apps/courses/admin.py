#import admin
from django.contrib import admin

#imports enrollment model
#import course models
from .models import Course, Enrollment, Assignment

#registers the following models on the admin site
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Assignment)