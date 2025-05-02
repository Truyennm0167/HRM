from django.shortcuts import render

# Create your views here.
def get_home(request):
    return render(request, 'hod_template/home_content.html')