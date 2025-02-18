from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name = "login"),
    path('logout/', views.logoutUser,  name = "logout" ),
    path('register/', views.register, name = "register"),
    path('add_user/', views.add_user, name = "add_user"),
    path('add_branch_page/', views.add_branch_page, name = "add_branch_page"),
    path('add_branch/', views.add_branch, name = "add_branch"),
    path('add_manufacturer_page/', views.add_manufacturer_page, name = "add_manufacturer_page"),

    path('add_manufacturer/', views.add_manufacturer, name = "add_manufacturer"),

    path('add_equipment_page/', views.add_equipment_page, name = "add_equipment_page"),

    path('add_equipment/', views.add_equipment, name = "add_equipment"),
    
    path('equipments/', views.equipment_list, name='equipment_list'),
    path('equipments/edit/<int:id>/', views.edit_equipment, name='edit_equipment'),

    path('add_spare_part_page/', views.add_spare_part_page, name = "add_spare_part_page"),

    path('add_spare_part/', views.add_spare_part, name = "add_spare_part"),
    
    path('spare_parts/', views.spare_part_list, name='spare_part_list'),
    path('spare_parts/edit/<int:id>/', views.edit_spare_part, name='edit_spare_part'),




    path('dashboard', views.dashboard, name="dashboard"),
    path('equipment/', views.equipment, name = "equipment"),
]