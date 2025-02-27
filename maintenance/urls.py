from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name = "login"),
    path('logout/', views.logoutUser,  name = "logout" ),
    # path('register/', views.register, name = "register"),
    # path('add_user/', views.add_user, name = "add_user"),
    # path('add_branch_page/', views.add_branch_page, name = "add_branch_page"),
    # path('add_branch/', views.add_branch, name = "add_branch"),
    #----------------------------------------------------------------------------------------------------
    path('add_manufacturer_page/', views.add_manufacturer_page, name = "add_manufacturer_page"),

    path('add_manufacturer/', views.add_manufacturer, name = "add_manufacturer"),

    path('manufacturer/', views.manufacturer_list, name='manufacturer_list'),
    path('manufacturer/edit/<int:id>/', views.edit_manufacturer, name='edit_manufacturer'),
    #-------------------------------------------------------------------------------------------------------

    path('add_equipment_page/', views.add_equipment_page, name = "add_equipment_page"),

    path('add_equipment/', views.add_equipment, name = "add_equipment"),
    
    path('equipments/', views.equipment_list, name='equipment_list'),
    path('equipments/edit/<int:id>/', views.edit_equipment, name='edit_equipment'),
    #---------------------------------------------------------------------------------------------------------

    path('add_spare_part_page/', views.add_spare_part_page, name = "add_spare_part_page"),

    path('add_spare_part/', views.add_spare_part, name = "add_spare_part"),
    
    path('spare_parts/', views.spare_part_list, name='spare_part_list'),
    path('spare_parts/edit/<int:id>/', views.edit_spare_part, name='edit_spare_part'),
    
    #---------------------------------------------------------------------------------------------------------
    
    path('add_chemical_page/', views.add_chemical_page, name = "add_chemical_page"),

    path('add_chemical/', views.add_chemical, name = "add_chemical"),
    
    path('chemicals/', views.chemical_list, name='chemical_list'),
    path('chemicals/edit/<int:id>/', views.edit_chemical, name='edit_chemical'),
    
    
    #----------------------------------------------------------------------------------------------
    path('add_maintenance_page/', views.add_maintenance_page, name = "add_maintenance_page"),

    path('add_maintenance/', views.add_maintenance, name = "add_maintenance"),
    
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/edit/<int:id>/', views.edit_maintenance, name='edit_maintenance'),
    
#--------------------------------------------------------------------------------------------------------

    path('add_work_order_page/', views.add_work_order_page, name = "add_work_order_page"),

    path('add_work_order/', views.add_work_order, name = "add_work_order"),
    
    path('work_order/', views.work_order_list, name='work_order_list'),
    path('work_order/edit/<int:id>/', views.edit_work_order, name='edit_work_order'),

#---------------------------------------------------------------------------------------------------------
path('add_spare_part_usage_page/', views.add_spare_part_usage_page, name = "add_spare_part_usage_page"),

    path('add_spare_part_usage/', views.add_spare_part_usage, name = "add_spare_part_usage"),
    
    path('spare_part_usage/', views.spare_part_usage_list, name='spare_part_usage_list'),
    path('spare_part_usage/edit/<int:id>/', views.edit_spare_part_usage, name='edit_spare_part_usage'),

#-----------------------------------------------------------------------------------------------------
path('add_decommissioned_equipment_page/', views.add_decommissioned_equipment_page, name = "add_decommissioned_equipment_page"),

    path('add_decommissioned_equipment/', views.add_decommissioned_equipment, name = "add_decommissioned_equipment"),
    
    path('decommissioned_equipment/', views.decommissioned_equipment_list, name='decommissioned_equipment_list'),
    path('decommissioned_equipment/edit/<int:id>/', views.edit_decommissioned_equipment, name='edit_decommissioned_equipment'),


#----------------------------------------------------------------------------------------------------------
path('add_maintenance_type_page/', views.add_maintenance_type_page, name = "add_maintenance_type_page"),

    path('add_maintenance_type/', views.add_maintenance_type, name = "add_maintenance_type"),
    
    path('maintenance_type/', views.maintenance_type_list, name='maintenance_type_list'),
    path('maintenance_type/edit/<int:id>/', views.edit_maintenance_type, name='edit_maintenance_type'),

#----------------------------------------------------------------------------------------------------------------

path('add_branch_page/', views.add_branch_page, name = "add_branch"),

    path('add_branch/', views.add_branch, name = "add_branch"),
    
    path('branch/', views.branch_list, name='branch_list'),
    path('branch/edit/<int:id>/', views.edit_branch, name='edit_branch'),

#---------------------------------------------------------------------------------------------------------
 path('my_profile/', views.my_profile, name='my_profile'),

path('add_user_profile_page/', views.add_user_profile_page, name = "add_user_profile_page"),

    path('add_user_profile/', views.add_user_profile, name = "add_user_profile"),
    
    path('user_profile/', views.user_profile_list, name='user_profile_list'),
    path('user_profile/edit/<int:id>/', views.edit_user_profile, name='edit_user_profile'),
     path('check-username/', views.check_username, name='check_username'),

    path('dashboard', views.dashboard, name="dashboard"),
    
    #-----------------------------------------------------------------------------------
 path('accept_maintenance/<int:maintenance_id>/', views.accept_maintenance, name='accept_maintenance'),
    path('complete_maintenance/<int:maintenance_id>/', views.complete_maintenance, name='complete_maintenance'),
    path('approve_maintenance/<int:maintenance_id>/', views.approve_maintenance, name='approve_maintenance'),    
    #-----------------------------------------------------------------------------------------------------------
    
    path('accept_work_order/<int:work_order_id>/', views.accept_work_order, name='accept_work_order'),
    path('complete_work_order/<int:work_order_id>/', views.complete_work_order, name='complete_work_order'),
    path('approve_work_order/<int:work_order_id>/', views.approve_work_order, name='approve_work_order'),    
    
    #-----------------------------------------------------------------------------------------------------------
    path('mark_notification_as_read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    
    path('maintenance_due/', views.maintenance_due, name='maintenance_due'),  
    
    path('low_spare_part/', views.low_spare_part, name='low_spare_part'),  

     path('restock_list/', views.restock_list, name='restock_list'),
    path('restock_spare_part/', views.restock_spare_part, name='restock_spare_part'),
        path('restock_spare_part_page/', views.restock_spare_part_page, name='restock_spare_part_page'),


#--------------------------------------------------------------------------------------------------------------------


path('chemical_usage/', views.chemical_usage, name= 'chemical_usage'),
path('chemical_usage_list/', views.chemical_usage_list, name= 'chemical_usage_list'),
 path('chemical_restock_list/', views.chemical_restock_list, name='chemical_restock_list'),
    path('restock_chemical/', views.restock_chemical, name='restock_chemical'),
    path('expiring_chemical/', views.expiring_chemical, name='expiring_chemical'),
]