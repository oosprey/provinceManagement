# coding: UTF-8
'''
Created on 2013-3-27

@author: tianwei
'''

from django.contrib import admin
from school.models import *


RegisterClass = (ProjectSingle,
                 PreSubmit,
                 FinalSubmit,
                 TechCompetition,
                 Patents,
                 Papers,
                 AchievementObjects,
                 UploadedFiles)

for item in RegisterClass:
    admin.site.register(item)