#!/usr/bin/python
# coding:UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2016-04-12 09:56
# Last modified: 2017-05-22 15:45
# Filename: ajax.py
# Description:
# coding: UTF-8
'''
Created on 2013-4-17

@author: sytmac
'''
import re
import time

from dajax.core import Dajax
from django.contrib.auth.models import User
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from django.utils import simplejson
from django.http import Http404
from school.models import ProjectSingle,Teacher_Enterprise,PreSubmitEnterprise
from school.forms import StudentDispatchForm
from school.views import Send_email_to_student, Count_email_already_exist, school_limit_num
from const.models import SchoolDict, ProjectCategory, FinancialCategory, InsituteCategory
from const import *
import datetime
from backend.logging import logger, loginfo
from backend.decorators import time_controller
from django.shortcuts import get_object_or_404
from school.utility import *
from users.models import SchoolProfile, StudentProfile
from adminStaff.forms import ProjectManageForm
from student.forms import StudentGroupForm, StudentGroupInfoForm
from student.models import Student_Group
from django.template.loader import render_to_string

@dajaxice_register
def setOver(request, pid):
    project = ProjectSingle.objects.get(project_id = pid)
    project.is_over = True
    project.save()
    return "ok"


@dajaxice_register
def  StudentDispatch(request, form):
    #dajax = Dajax()
    student_form =  StudentDispatchForm(deserialize_form(form))
    if student_form.is_valid():
        password = student_form.cleaned_data["student_password"]
        email = student_form.cleaned_data["student_email"]
        financial_cate = FINANCIAL_CATE_A
        #financial_cate = student_form.cleaned_data["proj_cate"]
        person_firstname = student_form.cleaned_data["person_firstname"]
        name = email
        if password == "":
            password = email.split('@')[0]
        #判断是否达到发送邮件的最大数量
        # email_num = Count_email_already_exist(request)
        # limited_num = school_limit_num(request)
        # remaining_activation_times = limited_num-email_num
        if False and remaining_activation_times==0:
            message = u"已经达到最大限度，无权发送"
            return simplejson.dumps({'field':student_form.data.keys(), 'status':'1', 'remaining_activation_times':remaining_activation_times, 'message':message})
        else:
            if financial_cate == FINANCIAL_CATE_A:
                #current_list = ProjectSingle.objects.filter(adminuser=request.user, year = get_current_year)
                school = get_object_or_404(SchoolProfile, userid=request.user).school

                # current_list = get_current_project_query_set().filter(school=school)
                # limits = ProjectPerLimits.objects.get(school__userid=request.user)
                # a_remainings = int(limits.a_cate_number) - len([project for project in current_list if project.financial_category.category == FINANCIAL_CATE_A])
                # if a_remainings <= 0:
                if False:
                    message = u"甲类项目达到最大限度，无权发送"
                    return simplejson.dumps({'field':student_form.data.keys(), 'status':'1', 'remaining_activation_times':remaining_activation_times, 'message':message})
            if financial_cate == FINANCIAL_CATE_B:
                school = get_object_or_404(SchoolProfile, userid=request.user).school
                # current_list = get_current_project_query_set().filter(school=school)
                # limits = ProjectPerLimits.objects.get(school__userid=request.user)
                # a_remainings = int(limits.a_cate_number) - len([project for project in current_list if project.financial_category.category == FINANCIAL_CATE_A])
                # b_remainings = int(limits.number) - int(limits.a_cate_number)
                # if b_remainings <= 0:
                if False:
                    message = u"乙类项目达到最大限度，无权发送"
                    return simplejson.dumps({'field':student_form.data.keys(), 'status':'1', 'remaining_activation_times':remaining_activation_times, 'message':message})

            flag, reason = Send_email_to_student(request, name, person_firstname,password, email,STUDENT_USER, financial_cate=financial_cate)
            if flag:
                message = u"发送邮件成功"
                # remaining_activation_times -= 1
                # return simplejson.dumps({'field':student_form.data.keys(), 'status':'1', 'message':message,'remaining_activation_times':remaining_activation_times})
                return simplejson.dumps({'field':student_form.data.keys(), 'status':'1', 'message':message})
            else:
                message = reason or u"邮件发送失败，请重新发送"
                # return simplejson.dumps({'field':student_form.data.keys(), 'status':'1', 'message':message,'remaining_activation_times':remaining_activation_times})
                return simplejson.dumps({'field':student_form.data.keys(), 'status':'1', 'message':message})
    else:
        logger.info("Form Valid Failed"+"**"*10)
        logger.info(student_form.errors)
        logger.info("--"*10)
        return simplejson.dumps({'field':student_form.data.keys(),'error_id':student_form.errors.keys(),'message':u"输入有误,请检查后重新发送"})

@dajaxice_register
def ProjCateChange(request, cate):
    #dajax = Dajax()
    try:
        project = ProjectSingle.objects.get(student__user=request.user)
        new_cate = ProjectCategory.objects.get(category=cate)
    except Exception, err:
        loginfo(p=err, label="change project cate")
        raise Http404
    project.project_category = new_cate
    project.save()
    return simplejson.dumps({"message": u"更新成功: %s" % new_cate})

@dajaxice_register
def ProjInsituteChange(request, cate):
    try:
        project = ProjectSingle.objects.get(student__user=request.user)
        new_cate = InsituteCategory.objects.get(category=cate)
    except Exception, err:
        loginfo(p=err, label="change project insitute")
        raise Http404
    project.insitute = new_cate
    project.save()
    return simplejson.dumps({"message": u"更新成功: %s" % new_cate})

@dajaxice_register
def FinancialCateChange(request, cate, pid):
    #dajax = Dajax()
    if cate == FINANCIAL_CATE_A:
        #current_list = ProjectSingle.objects.filter(adminuser=request.user, year = get_current_year)
        current_list = get_current_project_query_set().filter(adminuser = request.user)
        limits = ProjectPerLimits.objects.get(school__userid=request.user)
        a_remainings = int(limits.a_cate_number) - len([project for project in current_list if project.financial_category.category == FINANCIAL_CATE_A])
        if a_remainings <= 0:
            return simplejson.dumps({"message":u"甲类项目数量超额"})
    try:
        project = ProjectSingle.objects.get(project_id=pid)
        new_cate = FinancialCategory.objects.get(category=cate)
    except Exception, err:
        loginfo(p=err, label="change financial cate")
        raise Http404
    project.financial_category = new_cate
    project.save()
    return simplejson.dumps({"message": u"更新成功: %s" % new_cate})


@dajaxice_register
def FileDeleteConsistence(request, pid, fid):
    """
    Delete files in history file list
    """
    logger.info("sep delete files"+"**"*10)
    # check mapping relation
    f = get_object_or_404(UploadedFiles, file_id=fid)
    p = get_object_or_404(ProjectSingle, project_id=pid)

    logger.info(f.project_id.project_id)
    logger.info(p.project_id)

    if f.project_id.project_id != p.project_id:
        return simplejson.dumps({"is_deleted": False,
                                 "message": "Authority Failed!!!"})

    if request.method == "POST":
        f.delete()
        return simplejson.dumps({"is_deleted": True,
                                 "message": "delete it successfully!",
                                 "fid": str(fid)})
    else:
        return simplejson.dumps({"is_deleted": False,
                                 "message": "Warning! Only POST accepted!"})

@dajaxice_register
def StudentDeleteConsistence(request, uid):
    """
    Delete student in history file list
    """
    logger.info("sep delete student"+"**"*10)
    # check mapping relation
    try:
        delstudent=User.objects.get(id=uid)
        studentpro=StudentProfile.objects.get(user_id=uid)
        project=ProjectSingle.objects.get(student_id=studentpro.id)
        presubmitenterprise = PreSubmitEnterprise.objects.get(project_id_id=project.project_id)
        delteacher_enterprise=Teacher_Enterprise.objects.get(id=presubmitenterprise.enterpriseTeacher_id)
        if request.method == "POST":
            schooluser=request.user
            school=User.objects.get(username=schooluser)
            schoolpro=SchoolProfile.objects.filter(userid_id=school.id)
            if schoolpro:              
                if studentpro.school_id==schoolpro[0].id:
                    delstudent.delete()
                    delteacher_enterprise.delete()
                    return simplejson.dumps({"is_deleted": True,
                                 "message": "delete it successfully!",
                                 "uid": str(uid)})
        else:
            return simplejson.dumps({"is_deleted": False,
                                 "message": "Warning! Only POST accepted!"})
    except Exception, err:
        logger.info(err)

@dajaxice_register
def MemberChangeInfo(request, form, origin):
    loginfo(p=origin, label="origin")
    try:
        project = ProjectSingle.objects.get(student__user_id=request.user)
    except:
        raise Http404
    stugroup_form = StudentGroupInfoForm(deserialize_form(form))
    loginfo(p=stugroup_form, label="stugroup_form")
    if not stugroup_form.is_valid():
        ret = {'status': '1',
               'message': u"输入有误，请重新输入"}
    else:
        email = stugroup_form.cleaned_data["email"]
        telephone = stugroup_form.cleaned_data["telephone"]
        classInfo = stugroup_form.cleaned_data["classInfo"]
        student_id= stugroup_form.cleaned_data["student_id"]
        group = project.student_group_set
        for student in group.all():
            if student.studentId == origin :
                print "save successfully"
                student.email = email
                student.telephone = telephone
                student.classInfo = classInfo
                student.studentId = student_id
                student.save()
                table = refresh_member_table(request)
                ret = {'status': '0', 'message': u"人员变更成功", 'table':table}
                break
        else:
            ret = {'status': '1', 'message': u"该成员不存在，请刷新页面"}
    return simplejson.dumps(ret)

@dajaxice_register
def MemberDelete(request, deleteId):
    try:
        project = ProjectSingle.objects.get(student__user_id=request.user)
    except:
        raise Http404
    group = project.student_group_set
    for student in group.all():
        if student.studentId == deleteId:
            student.delete()
            table = refresh_member_table(request)
            ret = {'status': '0', 'message': u"人员变更成功", 'table':table}
            break
    else:
        ret = {'status': '1', 'message': u"待删除成员不存在，请刷新页面"}
    return simplejson.dumps(ret)

@dajaxice_register
def MemberChange(request, form, origin):
    print 'MemberChange'
    loginfo(p=origin, label="origin")
    stugroup_form = StudentGroupForm(deserialize_form(form))
    if not stugroup_form.is_valid():
        ret = {'status': '2',
               'error_id': stugroup_form.errors.keys(),
               'message': u"输入有误，请重新输入"}
    elif not origin: # 添加或更新成员
        print 'add new member'
        ret = new_or_update_member(request, stugroup_form)
    else:  # 更换成员
        ret = change_member(request, stugroup_form, origin)
    return simplejson.dumps(ret)

@dajaxice_register
def change_project_code(request, pid, project_code):
    message = ""
    project = ProjectSingle.objects.get(project_id = pid)
    try:
        if ProjectSingle.objects.filter(project_code = project_code).count(): 
            raise
        project.project_code = project_code
        project.save()
    except:
        message = "error"
        return simplejson.dumps({"message": message})
    return simplejson.dumps({"message": message, "res": project_code})

def change_member(request, stugroup_form, origin):
    student_id = stugroup_form.cleaned_data["student_id"]
    student_name = stugroup_form.cleaned_data["student_name"]
    try:
        project = ProjectSingle.objects.get(student__user_id=request.user)
    except:
        raise Http404

    group = project.student_group_set
    managerid=StudentProfile.objects.get(id=project.student_id) #得到负责人的信息
    teammanager = User.objects.get(id=managerid.user_id)
    if filter(lambda x:x==student_id, [student.studentId for student in group.all()]):
        return {'status': '1', 'message': u"替换成员已存在队伍中，请选择删除"}

    loginfo(p=teammanager.first_name,label="teammanager.first_name")
    loginfo(p=student_name,label="student_name")    
    for student in group.all():
        if student.studentId == origin:
            # 如果是更改负责人的信息时需要将first_name内容更新
            if  student.studentName == teammanager.first_name:
                teammanager.first_name = student_name
            student.studentName = student_name
            student.studentId = student_id
            student.save()
            table = refresh_member_table(request)
            ret = {'status': '0', 'message': u"人员变更成功", 'table':table}
            break
    else: # new student
        ret = {'status': '1', 'message': u"输入有误，请刷新后重新输入"}
    return ret

def new_or_update_member(request, stugroup_form):
    print "new_or_update_member"
    student_id = stugroup_form.cleaned_data["student_id"]
    student_name = stugroup_form.cleaned_data["student_name"]
    try:
        project = ProjectSingle.objects.get(student__user_id=request.user)
        loginfo(p=project,label='project')
    except:
        raise Http404

    managerid=StudentProfile.objects.get(id=project.student_id) #得到负责人的信息
    teammanager = User.objects.get(id=managerid.user_id)
    group = project.student_group_set
    loginfo(p=group, label="group")
    loginfo(p=teammanager.first_name,label="teammanager first_name")
    loginfo(p=student_name,label="student_name")    
    for student in group.all():
        if student.studentId == student_id:
            if  student.studentName == teammanager.first_name:
                teammanager.first_name = student_name
                teammanager.save()
                loginfo(p=teammanager.first_name,label="teammanager first_name")
                loginfo(p=student_name,label="student_name") 
            student.studentName = student_name
            student.save()
            table = refresh_member_table(request)
            ret = {'status': '0', 'message': u"人员信息更新成功", 'table':table}
            break
    else: # new student
        if group.count() == MEMBER_NUM_LIMIT[project.project_category.category]:
            ret = {'status': '1', 'message': u"人员已满，不可添加"}
        else:
            new_student = Student_Group(studentId = student_id,
                                        studentName = student_name,
                                        project=project)
            new_student.save()
            table = refresh_member_table(request)
            ret = {'status': '0', 'message': u"人员添加成功", 'table':table}
    return  ret

def refresh_member_table(request):
    student_account = StudentProfile.objects.get(user_id = request.user)
    project = ProjectSingle.objects.get(student=student_account)
    student_group = Student_Group.objects.filter(project = project)
    student_group_info_form = StudentGroupInfoForm()

    return render_to_string("school/widgets/member_group_table.html",
                            {"student_group": student_group,
                             "student_group_info_form": student_group_info_form})


@dajaxice_register
def checkStudentSno(request):
    def check_no_space(x):
        return x.strip(" ") != ""
    message = ""
    url = ""
    status = 0
    try:
        student = StudentProfile.objects.get(user = request.user)
        project =  ProjectSingle.objects.get(student = student)
        stu_set = Student_Group.objects.filter(project = project)
        for stu in stu_set:
            if check_no_space(stu.studentId) and check_no_space(stu.studentName):
                status = 1
                url = "/school/application/"+str(project.project_id)
                print url
            else:
                message = "不能填写申请书，请完善学号内容"
        if stu_set.count() == 0:
            message = "不能填写申请书，请先完善团队成员信息"
    except Exception,e:
            message = "学生信息验证失败"
            print e
    return simplejson.dumps({"status":status,"message":message,"url":url})


@dajaxice_register
def update_project_grade(request, grade_num, project_id):
    """
    Update project grade by choice.

    Return code non-zero means there is something wrong. The project grade
    will be updated only if the remaining count of that grade > 0.

    Author: David
    """
    is_expired = not time_controller(phase=STATUS_PRESUBMIT).check_day()
    if is_expired:
        return simplejson.dumps({'status': 5})
    try:
        if grade_num == '0':
            new_grade = ProjectGrade.objects.get(grade=GRADE_UN)
        elif grade_num == '1':
            new_grade = ProjectGrade.objects.get(grade=GRADE_PROVINCE)
        elif grade_num == '2':
            new_grade = ProjectGrade.objects.get(grade=GRADE_NATION)
        else:
            return simplejson.dumps({'status': 2})

        school = SchoolProfile.objects.get(userid=request.user)
        year = get_current_year()
        cur_list = ProjectSingle.objects.filter(school_id=school.school_id)
        cur_list = cur_list.filter(year=year)
        audited_list = []
        for project in cur_list:
            if project.project_category.category == 'innovation':
                if project.presubmit_set.all()[0].is_audited == True:
                    audited_list.append(project)
            else:
                if project.presubmitenterprise_set.all()[0].is_audited == True:
                    audited_list.append(project)
        cur_list = audited_list

        t, mp, mn, rp, rn = get_remain_grade_num(cur_list)
        if (grade_num == '1' and rp <= 0) or (grade_num == '2' and rn <= 0):
            return simplejson.dumps({'status': 4})

        proj = None
        for p in cur_list:
            if p.project_id == project_id:
                proj = p

        if proj is None:
            return simplejson.dumps({'status': 3})

        proj.project_grade = new_grade
        proj.save()
        return simplejson.dumps({'status': 0})
    except Exception, e:
        logger.info(e)
        return simplejson.dumps({'status': 1})


@dajaxice_register
def StudentsDispatch(request, emails):
    error_emails = []
    reasons = []
    datatuple = []
    for email, name in emails:
        student_form = StudentDispatchForm(
            {'student_email': email, 'person_firstname': name})
        if not student_form.is_valid():
            return simplejson.dumps({
                'status': 1, 'reason': student_form.errors.as_text(),
                'context': {'email': email, 'name': name}})
        password = student_form.cleaned_data["student_password"]
        email = student_form.cleaned_data["student_email"]
        financial_cate = FINANCIAL_CATE_A
        person_firstname = student_form.cleaned_data["person_firstname"]
        name = email
        if password == "":
            password = email.split('@')[0]
        # item = (name, person_firstname, password, email,
        #         STUDENT_USER, financial_cate)
        # datatuple.append(item)
        flag, reason = Send_email_to_student(
                request, name, person_firstname, password,
                email, STUDENT_USER, financial_cate=financial_cate)
        if not flag:
            error_emails.append(email)
            reasons.append(reason)
    if not error_emails:
        return simplejson.dumps({'status': 0})
    else:
        return simplejson.dumps({'status': 2, 'emails': error_emails,
                                 'reasons': reasons})
