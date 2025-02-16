from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name = "login"),
    path('logout/', views.logoutUser,  name = "logout" ),
    path('register/', views.register, name = "register"),
    path('Add_User/', views.Add_User, name = "Add_User"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('equipment/', views.equipment, name = "equipment"),
]