from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def test_login_view(request):
    return render(request, 'test_login.html')

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('test-login/', test_login_view, name='test_login'),
]
