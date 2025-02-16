from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name = "login"),
    path('logout/', views.logoutUser,  name = "logout" ),
    path('register/', views.register, name = "register"),
    path('Add_User/', views.Add_User, name = "Add_User"),
    path('add_branch_page/', views.add_branch_page, name = "add_branch_page"),
    path('add_branch/', views.add_branch, name = "add_branch"),


    path('dashboard', views.dashboard, name="dashboard"),
    path('equipment/', views.equipment, name = "equipment"),
]