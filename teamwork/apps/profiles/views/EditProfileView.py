# Model Imports
from teamwork.apps.profiles.models import Profile
# Form Imports
from teamwork.apps.profiles.forms import *
# View Imports
from teamwork.apps.profiles.views.ProfileView import view_profile
# Other
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect, JsonResponse)
from django.contrib import messages

import json

def edit_skills(request, username):
    if request.method == 'GET' and request.is_ajax():
        # JSON prefers dictionaries over lists.
        data = dict()
        # A list in a dictionary, accessed in select2 ajax
        data['items'] = []
        q = request.GET.get('q')
        if q is not None:
            results = Skills.objects.filter(
                Q( skill__contains = q ) ).order_by( 'skill' )
        for s in results:
            data['items'].append({'id': s.skill, 'text': s.skill})
        return JsonResponse(data)


    return HttpResponse("Failure")

@login_required
def edit_profile(request, username):
    """
    Public method that takes a request and a username.  Gets an entered 'skill' from the form
    and stores it in lowercase if it doesn't exist already. Renders profiles/edit_profile.html.

    GT OVERRRIDE DOES NOT EDIT OTHER PROFILES BUT IT NO LONGER CRASHES
    """
    if not request.user.is_authenticated:
        return redirect('profiles/profile.html')
    else:
        #grab profile for the current user
        profile = Profile.objects.prefetch_related('user').get(user=request.user)

    if request.user.username != username:
        messages.info(request, 'You cannot access the user profile specified!')
        return redirect(view_profile, request.user.username)

    page_name = "Edit Profile"
    page_description = "Edit %s's Profile"%(profile.user.username)
    title = "Edit Profile"

    #original form
    if request.method == 'POST':
        # Add skills to the project learn_skills
        if request.POST.get('known_skills') or request.POST.get('learn_skills'):
            known = request.POST.getlist('known_skills')
            learn = request.POST.getlist('learn_skills')
            if known:
                for s in known:
                    s_lower = s.lower()
                    # Check if lowercase version of skill is in db
                    if Skills.objects.filter(skill=s_lower):
                        # Skill already exists, then pull it up
                        known_skill = Skills.objects.get(skill=s_lower)
                    else:
                        # Add the new skill to the Skills table
                        known_skill = Skills.objects.create(skill=s_lower)
                        # Save the new object
                        known_skill.save()
                    # Add the skill to the project (as a desired_skill)
                    profile.known_skills.add(known_skill)
                    profile.save()
                # handles saving bio information also
                edit_profile_helper(request, username)
            if learn:
                for s in learn:
                    s_lower = s.lower()
                    # Check if lowercase version of skill is in db
                    if Skills.objects.filter(skill=s_lower):
                        # Skill already exists, then pull it up
                        learn_skill = Skills.objects.get(skill=s_lower)
                    else:
                        # Add the new skill to the Skills table
                        learn_skill = Skills.objects.create(skill=s_lower)
                        # Save the new object
                        learn_skill.save()
                    # Add the skill to the project (as a desired_skill)
                    profile.learn_skills.add(learn_skill)
                    profile.save()
                # handles saving bio information also
                edit_profile_helper(request, username)
            # stay on edit_profile page
            return redirect(edit_profile, username)

        # handle removing a known skill
        if request.POST.get('known_remove'):
            skillname = request.POST.get('known_remove')
            to_delete = Skills.objects.get(skill=skillname)
            profile.known_skills.remove(to_delete)

            # handles saving bio information also
            edit_profile_helper(request, username)
            # stay on edit_profile page
            return redirect(edit_profile, username)

        # handle removing a skill they wanted to learn
        if request.POST.get('learn_remove'):
            skillname = request.POST.get('learn_remove')
            to_delete = Skills.objects.get(skill=skillname)
            profile.learn_skills.remove(to_delete)

            # handles saving bio information also
            edit_profile_helper(request, username)
            # stay on edit_profile page
            return redirect(edit_profile, username)

        #handle deleting avatar
        if request.POST.get('delete_avatar'):
            avatar = request.POST.get('delete_avatar')
            profile.avatar.delete()
            form = ProfileForm(instance=profile)

        #handle deleting profile
        if request.POST.get('delete_profile'):
            page_user = get_object_or_404(User, username=username)

            if request.user.profile.isGT:
                page_user.delete()
                return redirect('view_course')
            else:
                page_user.delete()
                return redirect('about')

        # handles saving bio info if none of the cases were taken
        edit_profile_helper(request, username)

        #redirects to view_profile when submit button is clicked
        return redirect(view_profile, username)

    else:
        #load form with prepopulated data
        form = ProfileForm(instance=profile)

    known_skills_list = profile.known_skills.all()
    learn_skills_list = profile.learn_skills.all()

    return render(request, 'profiles/edit_profile.html', {
        'form':form, 'profile':profile,
        'known_skills_list':known_skills_list,
        'learn_skills_list':learn_skills_list, 'page_name' : page_name, 'page_description': page_description, 'title': title })

def edit_profile_helper(request, username):
    """
        Helper function that saves profile information from the ProfileForm
    """

    if request.user.profile.isGT:
        tempProfile = User.objects.get(username=username)
        profile = Profile.objects.get(user=tempProfile)
    else:
        #grab profile for the current user
        profile = Profile.objects.get(user=request.user)
        profileUser = User.objects.get(username=profile.user)
        #grab profile for the current user

    #request.FILES is passed for File storing
    form = ProfileForm(request.POST, request.FILES)
    if form.is_valid():

        # grab each form element from the clean form
        bio = form.cleaned_data.get('bio')
        email= form.cleaned_data.get('email')
        name = form.cleaned_data.get('name')
        institution = form.cleaned_data.get('institution')
        location = form.cleaned_data.get('location')
        ava = form.cleaned_data.get('avatar')

        #if data is entered, save it to the profile for the following
        if name:
            profile.name = name
        if email:
            profileUser.email = email
        if bio:
            profile.bio = bio
        if institution:
            profile.institution = institution
        if location:
            profile.location = location
        if ava:
            profile.avatar = ava

        profile.save()
        profileUser.save()
