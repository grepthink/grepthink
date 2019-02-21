# Django Modules
from django.contrib import admin

# Local Modules
from .models import Interest, Membership, Project, ProjectUpdate, ResourceUpdate, ProjectChat, Tsr, Techs

# Register the following models for the admin site
admin.site.register(Project)
<<<<<<< HEAD
<<<<<<< HEAD
=======
admin.site.unregister(Techs)
admin.site.register(Techs)
>>>>>>> 33b79e9... fixing env problem
=======

>>>>>>> 7e7f500... Merge pull request #2 from Hnguyen1997/Nikki
admin.site.register(Membership)
admin.site.register(ProjectUpdate)
admin.site.register(ResourceUpdate)
admin.site.register(Interest)
admin.site.register(ProjectChat)
admin.site.register(Tsr)
