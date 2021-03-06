#!/usr/local/bin/python3
# coding: UTF-8
# Author: David
# Email: youchen.du@gmail.com
# Created: 2017-04-20 09:29
# Last modified: 2017-04-26 14:48
# Filename: urls.py
# Description:
# coding: UTF-8
'''
Created on 2013-3-28

@author: tianwei

Desc: School URL defination
'''

from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *

from school import views as school_views


urlpatterns = patterns('',
    url(
        r'^$',
        school_views.home_view,
    ),
    url(
        r'^final/(?P<pid>.{36})$',
        school_views.final_report_view,
    ),
    url(
        r'^mid/(?P<pid>.{36})$',
        school_views.mid_report_view,
    ),
    url(
        r'^files/(?P<pid>.{36})$',
        school_views.file_view,
    ),

    url(
        r'^application/(?P<pid>.{36})$',
        school_views.application_report_view,
    ),
    #statistics
    url(
        r'^statistics/$',
        school_views.statistics_view,
    ),
    url(
        r'^new/$',
        school_views.new_report_view,
    ),
    url(
        r'^history/$',
        school_views.history_view,
    ),
    url(
        r'delete/(?P<pid>.{36})/(?P<fid>.{36})$',
        school_views.file_delete_view,
    ),
    url(
        r'non/$',
        school_views.non_authority_view,
    ),
    url(
        r'^dispatch/$',
        school_views.StudentDispatch,
    ),
    url(
        r'student/$',
        school_views.student_view,
    ),
    url(
        r'get_xls/$',
        school_views.get_xls,
    ), 
    url(
        r'auto_index/$',
        school_views.auto_index,
    ),
    url(
        r'^memberchange$',
        school_views.member_change,
    ),
    url(
        r'^assign_grade/$',
        school_views.assign_grade,
    ),
    url(
        r'^commitment_submit/$',
        school_views.commitment_submit,
        name='commitment_submit',
    ),
)

