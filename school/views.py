# coding: UTF-8
'''
Created on 2013-03-28

@author: tianwei

Desc: School's view, includes home(manage), final report,
      application report, statistics information.
'''
import datetime
import os
import sys
import uuid

from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponseForbidden, Http404, HttpResponseBadRequest
from django.template import RequestContext
from django.utils import simplejson
from django.views.decorators import csrf
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from school.models import ProjectSingle, PreSubmit, FinalSubmit
from school.models import UploadedFiles
from adminStaff.models import ProjectPerLimits
from users.models import SchoolProfile
from school import forms

from const.models import *
from const import *

from school.utility import *
from backend.logging import logger, loginfo
from backend.decorators import *
from adminStaff.views import AdminStaffService

@csrf.csrf_protect
@login_required
@authority_required(SCHOOL_USER)
def home_view(request):
    return render(request, "school/home.html", {})

@csrf.csrf_protect
@login_required
@authority_required(SCHOOL_USER)
def dispatch(request):
    teacher_form = forms.TeacherDispatchForm()
    expert_form = forms.ExpertDispatchForm()
    school = SchoolProfile.objects.get(userid=request.user)
    if not school:
        raise Http404

    email_list  = AdminStaffService.GetRegisterListBySchool(school)
    return render_to_response("school/dispatch.html",{'expert_form':expert_form, 'teacher_form':teacher_form, 'teacher_school' : school, 'email_list':email_list},context_instance=RequestContext(request))

@csrf.csrf_protect
@login_required
@authority_required(SCHOOL_USER)
def project_alloc(request):
    num_limit_form = forms.TeacherNumLimitForm(request=request)
    teacher_limit_num_list = teacherLimitNumList()
    context = {'num_limit_form': num_limit_form,
               'teacher_limit_num_list': teacher_limit_num_list}
    context.update(get_project_num_and_remaining(request))
    return render_to_response("school/projectlimitnumSettings.html",
                              context,
                              context_instance=RequestContext(request))

@csrf.csrf_protect
@login_required
@authority_required(SCHOOL_USER)
def get_project_num_and_remaining(request):
    teacher_list = TeacherProfile.objects.filter(school__userid=request.user)
    used_proj_num = sum([p.teacherprojectperlimits.number
                        for p in teacher_list \
                        if hasattr(p, 'teacherprojectperlimits')])

    try:
        limits = ProjectPerLimits.objects.get(school__userid=request.user)
    except Exception, err:
        logger.info(err)
        limits = None

    total = (limits and int(limits.number)) or 0
    remainings = (limits and (total - used_proj_num)) or 0
    context = dict((('projects_limit', total),
                    ('projects_remaining', remainings)))
    return context

def teacherLimitNumList():
    return TeacherProjectPerLimits.objects.all()
