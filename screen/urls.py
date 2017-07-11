# -*- coding: UTF-8 -*-
# author: star
# created_at: 17-6-27 12:25
from django.conf.urls import url, include

from .views import *

urlpatterns = [
    url(r'^group/$', group),
    url(r'^host/$', host),
    url(r'^interface', interface), 
    url(r"^warning/$", warning),
    url(r'^acknowledge/$', acknowledge),
    url(r'^graph/$', graph),
    url(r'^item/$', item),
    url(r'^history/$', history),
    url(r'^screen/$', screen),
    url(r'^follow/$', follow_list),
    url(r'^follow/create/$', follow_create),
    url(r'^follow/delete/$', follow_delete),
]
