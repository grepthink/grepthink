# Django Modules
from django.contrib import admin

# Local Modules
from .models import Interest, Membership, Project, ProjectUpdate, ResourceUpdate, ProjectChat, Tsr, Techs

# Register the following models for the admin site
admin.site.register(Project)
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
admin.site.unregister(Techs)
admin.site.register(Techs)
>>>>>>> 33b79e9... fixing env problem
=======

<<<<<<< HEAD
>>>>>>> 7e7f500... Merge pull request #2 from Hnguyen1997/Nikki
=======

=======
>>>>>>> a88ad43... Merge pull request #1 from Hnguyen1997/Anisha
admin.site.unregister(Techs)
admin.site.register(Techs)



<<<<<<< HEAD
>>>>>>> 9f4e50f... Merge branch 'master' into Anisha
=======
>>>>>>> a88ad43... Merge pull request #1 from Hnguyen1997/Anisha
admin.site.register(Membership)
admin.site.register(ProjectUpdate)
admin.site.register(ResourceUpdate)
admin.site.register(Interest)
admin.site.register(ProjectChat)
admin.site.register(Tsr)
