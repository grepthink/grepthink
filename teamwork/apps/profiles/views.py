from .models import *
from .forms import *

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from teamwork.apps.profiles.forms import SignUpForm



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'profiles/signup.html',
                          {'form': form})

        else:
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            prof = form.cleaned_data.get('prof')

            user1 = User.objects.create_user(username=username, password=password,
                                     email=email)
            user = authenticate(username=username, password=password)
            login(request, user)

            # saves current user, which creates a link from user to profile
            user1.save()

            # edits profile to add professor
            user1.profile.isProf = prof

            # saves profile
            user1.save()

            #User.objects.save()


            #uinfo = user.get_profile()
            #uinfo.isProf = prof
            #uinfo.save()

            return redirect('/')

    else:
        return render(request, 'profiles/signup.html',
                      {'form': SignUpForm()})

@login_required
def view_profile(request, username):
    """
    Public method that takes a request and a username.  Gets an entered 'skill' from the form
    and stores it in lowercase if it doesn't exist already. Renders profiles/profile.html.

    """
    profile = Profile.objects.get(user=request.user)

    page_user = get_object_or_404(User, username=username)
    return render(request, 'profiles/profile.html', {
        'page_user': page_user, 'profile':profile 
        })


@login_required
def edit_profile(request, username):
    """
    Public method that takes a request and a username.  Gets an entered 'skill' from the form
    and stores it in lowercase if it doesn't exist already. Renders profiles/edit_profile.html.

    TODO: screen flashes when deleting skills? Maybe pc just blows
    TODO: test different uses of profile.save(), i.e not so many god damn times
    TODO: Avatar doesn't show current file.url

    """
    if not request.user.is_authenticated:
        return redirect('profiles/profile.html')

    #grab profile for the current user
    profile = Profile.objects.get(user=request.user)        

    #handle deleting known_skills
    if request.POST.get('delete_known'):        
        skillname = request.POST.get('delete_known')
        to_delete = Skills.objects.get(skill=skillname)
        profile.known_skills.remove(to_delete)
        form = ProfileForm(instance=profile)

    #handle deleting learn_skills
    elif request.POST.get('delete_learn'):        
        skillname = request.POST.get('delete_learn')
        to_delete = Skills.objects.get(skill=skillname)
        profile.learn_skills.remove(to_delete)
        form = ProfileForm(instance=profile)
        
    #original form
    elif request.method == 'POST':     
        #request.FILES is passed for File storing              
        form = ProfileForm(request.POST, request.FILES)    
        if form.is_valid():   
            # grab each form element from the clean form         
            known = form.cleaned_data.get('known_skill')
            learn = form.cleaned_data.get('learn_skill')
            bio = form.cleaned_data.get('bio')
            name = form.cleaned_data.get('name')
            institution = form.cleaned_data.get('institution')
            location = form.cleaned_data.get('location')
            ava = form.cleaned_data.get('avatar')
            
            # if we have an input in known_skills 
            if known:
                # parse known on ','
                skill_array = known.split(',')
                for skill in skill_array:                    
                    stripped_skill = skill.strip()
                    if not (stripped_skill == ""):
                        # check if skill is in Skills table, lower standardizes input
                        if Skills.objects.filter(skill=stripped_skill.lower()):
                            # skill already exists, then pull it up  
                            known_skill = Skills.objects.get(skill=stripped_skill.lower()) 
                        else:
                            # we have to add the skill to the table
                            known_skill = Skills.objects.create(skill=stripped_skill.lower())
                            # save the new object
                            known_skill.save()
        
                        # add the skill to the current profile
                        profile.known_skills.add(known_skill)
                        profile.save()                         
     

            # same as Known implemenation for learn_skills
            if learn:
                skill_array = learn.split(',')
                for skill in skill_array:                    
                    stripped_skill = skill.strip()
                    if not (stripped_skill == ""):                        
                        # check if skill is in Skills table, lower standardizes input
                        if Skills.objects.filter(skill=stripped_skill.lower()):
                            # skill already exists, then pull it up  
                            learn_skill = Skills.objects.get(skill=stripped_skill.lower()) 
                        else:
                            # we have to add the skill to the table
                            learn_skill = Skills.objects.create(skill=stripped_skill.lower())
                            # save the new object
                            learn_skill.save()                                    
                        profile.learn_skills.add(learn_skill)
                        profile.save()
            #if data is entered, save it to the profile for the following     
            if name:
                profile.name = name
                profile.save()
            if bio:
                profile.bio = bio                
                profile.save()
            if institution:
                profile.institution = institution
                profile.save()
            if location:
                profile.location = location
                profile.save()            
            if ava:                
                profile.avatar = ava                
                profile.save()   

        #redirects to view_profile when submit button is clicked
        return redirect(view_profile, username)             

    else:
        #load form with prepopulated data            
        form = ProfileForm(instance=profile)
        
    known_skills_list = profile.known_skills.all()
    learn_skills_list = profile.learn_skills.all()
    page_user = get_object_or_404(User, username=username)

    return render(request, 'profiles/edit_profile.html', {
        'page_user': page_user, 'form':form, 'profile':profile,
        'known_skills_list':known_skills_list,
        'learn_skills_list':learn_skills_list })
























