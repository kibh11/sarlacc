from django.urls import path
from . import views

urlpatterns = [
    path('data_input/', views.data_input, name='data_input'),
]
