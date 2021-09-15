from django.urls import path

from . import views

app_name = 'bot'
urlpatterns = [
    path('logs/', views.logs, name='logs'),
]