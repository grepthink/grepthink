from django.contrib.auth.decorators import login_required

"""
TODO: this view is going to be the intermediate view to give payment when creating a course
"""

@login_required
def pay_for_course(request):
    print("temp")

@login_required
def PayWallView(request):
    print("temp")
