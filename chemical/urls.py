from django.urls import path
from . import views

urlpatterns = [
path('add_chemical_page/', views.add_chemical_page, name = "add_chemical_page"),

path('add_chemical/', views.add_chemical, name = "add_chemical"),

path('chemicals/', views.chemical_list, name='chemical_list'),
path('chemicals/edit/<int:id>/', views.edit_chemical, name='edit_chemical'),
    
    
#----------------------------------------------------------------------------------------------


path('chemical_usage/', views.chemical_usage, name= 'chemical_usage'),
path('chemical_usage_list/', views.chemical_usage_list, name= 'chemical_usage_list'),
 path('chemical_restock_list/', views.chemical_restock_list, name='chemical_restock_list'),
    path('restock_chemical/', views.restock_chemical, name='restock_chemical'),
    path('expiring_chemical/', views.expiring_chemical, name='expiring_chemical'),

]