"""
Public URLs - No login required
Recruitment pages accessible to everyone
"""
from django.urls import path
from app import views

urlpatterns = [
    # Public Career Pages
    path('careers/', views.careers_list, name='careers_list'),
    path('careers/<int:job_id>/', views.careers_detail, name='careers_detail'),
    path('careers/<int:job_id>/apply/', views.careers_apply, name='careers_apply'),
]
