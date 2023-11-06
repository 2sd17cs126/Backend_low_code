from django.urls import path
from rest_framework import routers
from . import views 

urlpatterns=[
    path('',views.data_operation,name='home'),
    path('bdd',views.bdd),
    path('stepdefination',views.step_def),
    path('automatic',views.automatic),
    path('integrate',views.integrate),
    path('enhance',views.enhance),
    path('enhanced_step_def',views.enhanced_step_def),
    path('report',views.report),
    path('automatic_pre_post',views.automatic_pre_post),
    path('suggestions', views.get_suggestions),
    path('store_suggestions', views.store_suggestions),
    path('get_inputdata', views.get_inputdata),
    path('save_data', views.save_data),
    path('open_popup',views.open_popup),
    path('extract_page',views.extract_page),
    path('capture_xpath',views.capture_xpath),
    path('capture_label_xpath',views.capture_label_xpath),
    path('check_working',views.capture_working),
    path('automatic_fetch',views.automatic_fetch)
]