#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 22:03
# Last modified: 2017-04-20 10:27
# Filename: views.py
# Description:
# coding: UTF-8
'''
Created on 2013-04-02

@author: tianwei

Desc: Registration and login redirect
'''

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from registration.forms import RegistrationFormUniqueEmail
from registration.models import RegistrationProfile
from backend.decorators import check_auth
from const import *


def active(request, activation_key,
           template_name='registration/activate.html',
           extra_context=None):
    """
    Active the user account from an activation key.
    """
    activation_key = activation_key.lower()
    account = RegistrationProfile.objects.activate_user(activation_key)
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render_to_response(template_name,
                              {'account': account,
                               'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS
                               },
                              context_instance=context)


def register(request, success_url=None,
             form_class=RegistrationFormUniqueEmail, profile_callback=None,
             template_name='registration/registration_form.html',
             extra_context=None):
    """
     Allow a new user to register an account.
    """
    if request.method == "POST":
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_user = form.save(request, profile_callback=profile_callback)
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.
            return HttpResponseRedirect(success_url or reverse('registration_complete'))
    else:
        form = form_class()

    if extra_context is None:
        extra_context = {}

    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render_to_response(template_name,
                              {'form': form},
                              context_instance=context)

# def login_redirect(request):
#     """
#     When the user login, it will decide to jump the according page, in other
#     words, school user will be imported /school/ page, if the user have many
#     authorities, the system will jump randomly
#     """
#     #TODO: I will use reverse function to redirect, like school and expert
#     if check_auth(request.user, SCHOOL_USER):
#         return HttpResponseRedirect(reverse('school.views.home_view'))
#     elif check_auth(request.user, STUDENT_USER):
#         return HttpResponseRedirect(reverse('school.views.student_view'))
#     elif check_auth(request.user, EXPERT_USER):
#         return HttpResponseRedirect(reverse('expert.views.home_view'))
#     elif check_auth(request.user, ADMINSTAFF_USER):
#         return HttpResponseRedirect('/adminStaff/')
#     else:
#         return HttpResponseRedirect('/')

def provincelogin_redirect(request): 
    """
    When the user login, it will decide to jump the according page, in other
    words, school user will be imported /school/ page, if the user have many
    authorities, the system will jump randomly
    """
    if check_auth(request.user, ADMINSTAFF_USER):
        return HttpResponseRedirect('/adminStaff/')
    else:
        logout(request)
        return render_to_response('registration/logentry_error.html', context_instance=RequestContext(request))

def schoollogin_redirect(request): 
    """
    When the user login, it will decide to jump the according page, in other
    words, school user will be imported /school/ page, if the user have many
    authorities, the system will jump randomly
    """
    if check_auth(request.user, SCHOOL_USER):
        return HttpResponseRedirect(reverse('school.views.home_view'))
    else:
        logout(request)
        return render_to_response('registration/logentry_error.html', context_instance=RequestContext(request))


def expertlogin_redirect(request): 
    """
    When the user login, it will decide to jump the according page, in other
    words, school user will be imported /school/ page, if the user have many
    authorities, the system will jump randomly
    """
    if check_auth(request.user, EXPERT_USER):
        return HttpResponseRedirect(reverse('expert.views.home_view'))
    else:
        logout(request)
        return render_to_response('registration/logentry_error.html', context_instance=RequestContext(request))


def studentlogin_redirect(request): 
    """
    When the user login, it will decide to jump the according page, in other
    words, school user will be imported /school/ page, if the user have many
    authorities, the system will jump randomly
    """
    if check_auth(request.user, STUDENT_USER):
        return HttpResponseRedirect(reverse('school.views.student_view'))
    else:
        logout(request)
        return render_to_response('registration/logentry_error.html', context_instance=RequestContext(request))


def identity_redirect(request):
    """
    Redirect user based on identity.

    Author: David
    """
    if check_auth(request.user, ADMINSTAFF_USER):
        return HttpResponseRedirect('/adminStaff/')
    elif check_auth(request.user, SCHOOL_USER):
        return HttpResponseRedirect(reverse('school.views.home_view'))
    elif check_auth(request.user, EXPERT_USER):
        return HttpResponseRedirect(reverse('expert.views.home_view'))
    elif check_auth(request.user, STUDENT_USER):
        return HttpResponseRedirect(reverse('school.views.student_view'))
    else:
        logout(request)
        return render_to_response('registration/logentry_error.html', context_instance=RequestContext(request))
