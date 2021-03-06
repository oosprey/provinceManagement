# Create your views here.
#
from school.models import *
from const.models import ProjectGrade
from django.http import Http404
from django.db.models import Q
from django.shortcuts import render
from backend.utility import convert2media_url, getContext
from const import PROJECT_GRADE_CHOICES, GRADE_NATION, DEFAULT_IMG_URL
from const.models import SchoolDict, ProjectGrade

from backend.logging import logger, loginfo

GRADE_DICT = dict(PROJECT_GRADE_CHOICES)

def show_project(request, project_id = ""):
    context = show_project_common(request,project_id, new_show = False)
    return render(request, 'showtime/showtime.html', context)

def show_project_new(request, project_id = ""):
    context = show_project_common(request,project_id,new_show = True)
    return render(request, 'showtime/showtime.html', context)

def show_project_common(request,project_id,new_show = False):
    if new_show:
        project = ShowProjectSingle.objects.get(project_id = project_id)
        imgs = project.showfiles_set.filter(
            Q(file_obj__iendswith="jpg") | \
            Q(file_obj__iendswith="png")
        )
        project.summary = project.result_overview
    else:
        project = ProjectSingle.objects.get(project_id = project_id)
        imgs = project.uploadedfiles_set.filter(
            Q(file_obj__iendswith="jpg") | \
            Q(file_obj__iendswith="png")
        )
        presubmit = project.presubmit_set.all()
        presubmit = presubmit.count() and presubmit[0] or None

        finalsubmit = project.finalsubmit_set.all()
        finalsubmit = finalsubmit.count() and finalsubmit[0] or None
        project.background = presubmit and presubmit.background or None
        project.summary = finalsubmit and finalsubmit.achievement_summary or None
    
    imgs = map(lambda x: convert2media_url(x.file_obj.url), imgs)
    first_img = (len(imgs) and imgs[0]) or DEFAULT_IMG_URL

    context = {"project": project,
               "imgs": imgs,
               "first_img": first_img
            }
    return context 

def show_index(request):
    context = common_show(request)
    return render(request, 'introduction/show.html', context)

def show_index_new(request):
    context = common_show(request,new_show = True)
    return render(request, 'introduction/show.html', context)

def common_show(request,new_show = False):
    project_page = request.GET.get('project_page')
    try:
        project_page = int(project_page)
    except:
        project_page = 1
    if project_page <= 0:
        raise Http404

    context = show_index_get_context(request, project_page,new_show)
    return context

def show_index_get_context(request, project_page,new_show):
    context = show_index_get_search_context(request, project_page,new_show)
    if project_page != context["project_page"].number:
        raise Http404
    for project in context["project_list"]:
        if new_show:
            imgs = project.showfiles_set.filter( \
                Q(file_obj__iendswith="jpg") | \
                Q(file_obj__iendswith="png") )
        else:
            imgs = project.uploadedfiles_set.filter( \
                Q(file_obj__iendswith="jpg") | \
                Q(file_obj__iendswith="png") )
        project.img = (imgs.count() and convert2media_url(imgs[0].file_obj.url)) or \
            DEFAULT_IMG_URL

    yearset = set()
    for project in ProjectSingle.objects.all():
        yearset.add(project.year)

    context["years"] = list(yearset)
    context["schools"] = SchoolDict.objects.all()
    context["grades"] = ProjectGrade.objects.all()

    return context

def show_index_get_search_context(request, project_page,new_show = False):
    search_school = request.GET.get('search_school') or ""
    search_year = request.GET.get('search_year') or ""
    search_grade = request.GET.get('search_grade') or ""
    search_keywords=request.GET.get('search_keywords') or ""
    pro_type = ShowProjectSingle if new_show else ProjectSingle
    
    q1 = (search_year and Q(year=search_year)) or None
    q2 = (search_school and Q(school=search_school)) or None
    q3 = (search_grade and Q(project_grade=search_grade)) or None
    q4 = (search_keywords and  (Q(keywords__icontains=search_keywords) | \
            Q(title__icontains=search_keywords) | Q(background__icontains=search_keywords) \
            | Q(result_overview__icontains=search_keywords))) or None
    qset = filter(lambda x: x != None, [q1, q2, q3,q4])
    loginfo(p=q4, label="in q4")
    loginfo(p=qset, label="in qset")
    if qset:
        qset = reduce(lambda x, y: x & y, qset)
        project_list = pro_type.objects.filter(qset)
    else:
        project_list = pro_type.objects.all()

    context = getContext(project_list, project_page, 'project', page_elems=9)
    context["search_school"] = search_school
    context["search_year"] = search_year
    context["search_grade"] = search_grade

    return context
