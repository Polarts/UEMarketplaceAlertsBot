from os import name
from django.urls import path

from . import views

app_name = 'bot'
urlpatterns = [
    path('logs/', views.logs, name='logs'),
    path('state/', views.get_app_state, name='state'),
    path('state/<newState>', views.set_app_state, name='set-state'),
]