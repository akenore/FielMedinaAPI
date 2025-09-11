from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'api/views/index.html')

def login(request):
    return render(request, 'api/auth/login.html')

def register(request):
    return render(request, 'api/auth/register.html')