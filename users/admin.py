# -*- coding: UTF-8 -*-
'''
Created on 2012-11-5

@author: tianwei
'''

from django.contrib import admin
from users.models import *


RegisterClass = (SchoolProfile,
                 ExpertProfile,
                 AdminStaffProfile,
                 AuthorityRelation)

for item in RegisterClass:
    admin.site.register(item)
