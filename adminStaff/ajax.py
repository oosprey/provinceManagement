# coding: UTF-8
'''
Created on 2013-3-29

@author: sytmac
'''

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from django.utils import simplejson
from adminStaff.forms import NumLimitForm, TimeSettingForm, SubjectCategoryForm, ExpertDispatchForm, SchoolDispatchForm
from adminStaff.models import  ProjectPerLimits, ProjectControl
from const.models import SchoolDict
from const import *
from adminStaff.utils import DateFormatTransfer
from adminStaff.views import AdminStaffService
from school.models import Project_Is_Assigned, InsituteCategory
from users.models import SchoolProfile

@dajaxice_register
def NumLimit(request, form):
    dajax = Dajax()
    form = NumLimitForm(deserialize_form(form))
    if form.is_valid():
        school = SchoolDict.objects.get(id=form.cleaned_data["school_name"])
        limited_num = form.cleaned_data["limited_num"]
        try:
            school_obj = SchoolProfile.objects.get(school=school)
            if  ProjectPerLimits.objects.filter(school=school_obj).count() == 0 :
                projectlimit = ProjectPerLimits(school=school_obj,
                                                   number=limited_num)
                projectlimit.save()
            else:
                object = ProjectPerLimits.objects.get(school=school_obj)
                object.number = limited_num
                object.save()
            return simplejson.dumps({'status':'1','message':u'更新成功'})
        except SchoolProfile.DoesNotExist:
            return simplejson.dumps({'status':'1','message':u'更新失败，选定的学校没有进行注册'})
    else:
        return simplejson.dumps({'id':form.errors.keys(),'message':u'输入错误'})
    
@dajaxice_register
def DeadlineSettings(request, form):
    #dajax = Dajax()
    form = TimeSettingForm(deserialize_form(form))
    if form.is_valid():
        # get cleaned_data
        psd = DateFormatTransfer(form.data["pre_start_date"])
        ped = DateFormatTransfer(form.data["pre_end_date"])
        fsd = DateFormatTransfer(form.data["final_start_date"])
        fed = DateFormatTransfer(form.data["final_end_date"])
        psdr = DateFormatTransfer(form.data["pre_start_date_review"])
        pedr = DateFormatTransfer(form.data["pre_end_date_review"])
        fsdr = DateFormatTransfer(form.data["final_start_date_review"])
        fedr = DateFormatTransfer(form.data["final_end_date_review"])
        # if object exists ,then obtain the object and update it
        if ProjectControl.objects.count() == 0:
            try:
                ProjectControl(pre_start_day=psd,
                               pre_end_day=ped,
                               final_start_day=fsd,
                               final_end_day=fed,
                               pre_start_day_review=psdr,
                               pre_end_day_review=pedr,
                               final_start_day_review=fsdr,
                               final_end_day_review=fedr).save()
            except:
                return simplejson.dumps({'field':form.data.keys(),'error_id':form.errors.keys(),'message':u"输入数据有误格式为YYYY-MM-DD"})
        else:
            try:
                object = ProjectControl.objects.get()
                object.pre_start_day = psd
                object.pre_end_day = ped
                object.final_start_day = fsd
                object.final_end_day = fed
                object.pre_start_day_review = psdr
                object.pre_end_day_review = pedr
                object.final_start_day_review = fsdr
                object.final_end_day_review = fedr
                object.save()
            except:
                return simplejson.dumps({'field':form.data.keys(),'error_id':form.errors.keys(),'message':u"输入数据有误格式为YYYY-MM-DD"})
        return simplejson.dumps({'field':form.data.keys(),'status':'1','message':u'更新成功'})
        #return simplejson.dumps({'field':form.data["pre_start_date"],'id':form,'status':'1','message':u'更新成功'})
    else:
        return simplejson.dumps({'field':form.data.keys(),'error_id':form.errors.keys(),'message':u"输入有误"})
    
@dajaxice_register
def  ExpertDispatch(request, form):
    #dajax = Dajax()
    expert_form =  ExpertDispatchForm(deserialize_form(form))
    if expert_form.is_valid():
        password = expert_form.cleaned_data["expert_password"]
        email = expert_form.cleaned_data["expert_email"]
        name = email
        if password == "":
            password = email.split('@')[0]
        flag = AdminStaffService.sendemail(request, name, password, email,EXPERT_USER)
        if flag:
            message = u"发送邮件成功"
            return simplejson.dumps({'field':expert_form.data.keys(), 'status':'1', 'message':message})
        else:
            message = u"相同邮件已经发送，中断发送"
            return simplejson.dumps({'field':expert_form.data.keys(), 'status':'1', 'message':message})
    else:
        return simplejson.dumps({'field':expert_form.data.keys(),'error_id':form.errors.keys(),'message':u"输入有误,请检查邮箱的合法性"})
@dajaxice_register
def SchoolDispatch(request, form):
    #dajax = Dajax()
    school_form = SchoolDispatchForm(deserialize_form(form))
    if school_form.is_valid():
        password = school_form.cleaned_data["school_password"]
        email = school_form.cleaned_data["school_email"]
        name = email
        school_name = school_form.cleaned_data["school_name"]
        if password == "":
            password = email.split('@')[0]
        flag = AdminStaffService.sendemail(request, name, password, email,SCHOOL_USER, school_name=school_name)
        if flag:
            message = u"发送邮件成功"
            return simplejson.dumps({'field':school_form.data.keys(), 'status':'1', 'message':message})
        else:
            message = u"相同邮件已经发送，中断发送"
            return simplejson.dumps({'field':school_form.data.keys(), 'status':'1', 'message':message})
    else:
        return simplejson.dumps({'id':school_form.errors.keys(),'message':u"输入有误,请检查邮箱的合法性"})
@dajaxice_register
def judge_is_assigned(request,insitute):
    '''
    to judge if the projects that belong to the certain insitute has been assigned
    '''
    #dajax = Dajax()
    #query database
    try:
        insobj = InsituteCategory.objects.get(id=insitute)
    except InsituteCategory.DoesNotExist:
        return simplejson.dumps({'flag':None,'message':u"InstituteCategory 数据不完全，请更新数据库"})
    try:
        obj = Project_Is_Assigned.objects.get(insitute = insobj)
    except Project_Is_Assigned.DoesNotExist:
        return simplejson.dumps({'flag':None,'message':u"Project_Is_Assigned 数据不完全，请更新数据库"})
    return simplejson.dumps({'flag':obj.is_assigned})

@dajaxice_register
def get_subject_review_list(request, project_id):
    '''
    to get subject evaluate list through project_id 
    '''
    #dajax = Dajax()
    review_list = AdminStaffService.GetSubjectReviewList(project_id)

    return simplejson.dumps({'review_list':review_list})

@dajaxice_register
def change_subject_grade(request, project_id, changed_grade):
    '''
    change subject grade secretly
    '''
    AdminStaffService.SubjectGradeChange(project_id, changed_grade)
    return simplejson.dumps({'status':'1'})

    