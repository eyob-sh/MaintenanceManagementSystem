from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import Http404

from django.contrib.auth import authenticate, login, logout
# Create your views here.


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def custom_403_view(request, exception):
    return render(request, '404.html', status=403)


def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # try:
        #     user = user.objects.get(username = username)
        
        # except: 
        #     messages.error(request, 'user does not exist')


        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else: 
            messages.error(request, 'Incorrect Username or Password')
        
    context = {}
    return render(request, 'login_page.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


def register(request):
    return render(request,'register_page.html')


def Add_User(request):
    return render(request,'register_page.html')



@login_required()
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required()
def equipment(request):
    return render(request, 'equipment.html')