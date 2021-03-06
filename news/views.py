#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-19 22:14
# Last modified: 2017-04-19 22:14
# Filename: views.py
# Description:
# coding: UTF-8
'''
Created on 2013-03-17

@author: Tianwei

Desc: news view with Tinymce
'''
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render #, render_to_response

from news.models import News
from django.template import Context #, loader
from django.http import HttpResponse, Http404
from backend.utility import getContext, getSchoolsPic
import datetime, os
from const import *
from const.models import *
from backend.logging import logger, loginfo

def get_news(news_id = None):
    if news_id: #get news which id equal to news_id
        try:
            news_content = News.objects.get(id = news_id)
        except:
            raise Http404
    else: # get latest news
        news_content = (News.objects.count() and News.objects.order_by('-news_date')[0]) or None
    return news_content

def index(request):
    '''
    for index_new
    '''
    news_announcement = News.objects.filter(news_category__category=NEWS_CATEGORY_ANNOUNCEMENT).order_by('-news_date')
    # news_policy = News.objects.filter(news_category__category=NEWS_CATEGORY_POLICY).order_by('-news_date')
    news_dynamic = News.objects.filter(news_category__category=NEWS_CATEGORY_DYNAMIC).order_by('-news_date')
    news_outstanding = News.objects.filter(news_category__category=NEWS_CATEGORY_OUTSTANDING).order_by('-news_date')
    news_others = News.objects.filter(news_category__category=NEWS_CATEGORY_OTHERS).order_by('-news_date')
    context = getContext(news_announcement, 1, "news_announcement", page_elems=8)
    # context.update(getContext(news_policy, 1, "news_policy", page_elems=8))
    context.update(getContext(news_dynamic, 1, "news_dynamic", page_elems=8))
    context.update(getContext(news_outstanding, 1, "news_outstanding", page_elems=8))
    context.update(getContext(news_others, 1, "news_others", page_elems=8))
    return context
    # return render(request, 'home/index.html', context)


def index_new(request):
    names = getSchoolsPic()
    context = {"schools_name_list": names}
    context.update(index(request))
    news_cate = {}
    news_cate["news_category_announcement"] = NEWS_CATEGORY_ANNOUNCEMENT
    news_cate["news_category_dynamic"] = NEWS_CATEGORY_DYNAMIC
    # news_cate["news_category_policy"] = NEWS_CATEGORY_POLICY
    news_cate["news_category_others"] = NEWS_CATEGORY_OTHERS
    news_cate["news_category_outstanding"] = NEWS_CATEGORY_OUTSTANDING
    context.update(news_cate)
    return render(request, "home/new-homepage.html", context)


def read_news(request, news_id):
    news = get_news(news_id)
    news_cate = news.news_category
    context = Context({
        'news': news,
        'news_cate':news_cate,
        '%s_active' % news_cate.category: 'active',
    })
    return render(request, 'home/news-content.html', context)

def list_news_by_cate(request, news_cate):
    try:
        if news_cate == NEWS_CATEGORY_DOCUMENTS:
            news_list = News.objects.exclude(news_document=u'').order_by('-news_date')
        else:
            news_list = News.objects.filter(news_category__category=news_cate).order_by('-news_date')
            news_cate = NewsCategory.objects.get(category=news_cate)
    except:
        raise Http404
    news_page = request.GET.get('news_page')
    context = getContext(news_list, news_page, 'news')
    if not news_cate == NEWS_CATEGORY_DOCUMENTS:
        context["news_cate"] = news_cate
        context['%s_active' % news_cate.category] = 'active'
    return render(request, 'home/news-list-by-cate.html', \
                  Context(context))
def list_news(request):
    news_list = News.objects.order_by('-news_date')
    news_page = request.GET.get('news_page')

    docs_list = news_list.exclude(news_document=u'')
    docs_page = request.GET.get('docs_page')

    context = getContext(news_list, news_page, 'news')
    context.update(getContext(docs_list, docs_page, 'docs'))
    return render(request, 'home/news-list.html', \
                  Context(context))


def download_news_doc(request, news_id):
    news_doc_name = get_news(news_id).news_document.path
    def readFile(fn, buf_size=DOWNLOAD_BUF_SIZE):
        f = open(fn, "rb")
        while True:
            _c = f.read(buf_size)
            if _c:
                yield _c
            else:
                break
        f.close()
    response = HttpResponse(readFile(news_doc_name), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(news_doc_name).encode("UTF-8") #NOTICE: the file must be unicode
    return response
