from django.urls import path
from . import views
from django.views.generic.base import RedirectView


urlpatterns = [
path('', RedirectView.as_view(url='/login/', permanent=True)),
path('login/', views.loginPage, name = "login"),
path('logout/', views.logoutUser,  name = "logout" ),
# path('register/', views.register, name = "register"),
# path('add_user/', views.add_user, name = "add_user"),
# path('add_branch_page/', views.add_branch_page, name = "add_branch_page"),
# path('add_branch/', views.add_branch, name = "add_branch"),
#----------------------------------------------------------------------------------------------------

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



    
    path('add_manufacturer_page/', views.add_manufacturer_page, name = "add_manufacturer_page"),

    path('add_manufacturer/', views.add_manufacturer, name = "add_manufacturer"),

    path('manufacturer/', views.manufacturer_list, name='manufacturer_list'),
    path('manufacturer/edit/<int:id>/', views.edit_manufacturer, name='edit_manufacturer'),
    path('manufacturer/delete/<int:id>/',views.delete_manufacturer, name = 'delete_manufacturer'),
    #-------------------------------------------------------------------------------------------------------

    path('add_equipment_page/', views.add_equipment_page, name = "add_equipment_page"),

    path('add_equipment/', views.add_equipment, name = "add_equipment"),
    
    path('equipments/', views.equipment_list, name='equipment_list'),
    path('equipments/edit/<int:id>/', views.edit_equipment, name='edit_equipment'),
    path('equipment/delete/<int:id>/',views.delete_equipment, name = 'delete_equipment'),

    #---------------------------------------------------------------------------------------------------------

    path('add_spare_part_page/', views.add_spare_part_page, name = "add_spare_part_page"),

    path('add_spare_part/', views.add_spare_part, name = "add_spare_part"),
    
    path('spare_parts/', views.spare_part_list, name='spare_part_list'),
    path('spare_parts/edit/<int:id>/', views.edit_spare_part, name='edit_spare_part'),
    
    #---------------------------------------------------------------------------------------------------------
    
    
    path('add_maintenance_page/', views.add_maintenance_page, name = "add_maintenance_page"),

    path('add_maintenance/', views.add_maintenance, name = "add_maintenance"),
    
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/edit/<int:id>/', views.edit_maintenance, name='edit_maintenance'),
    path('maintenance/delete/<int:id>/',views.delete_maintenance, name = 'delete_maintenance'),
    path('get-tasks/', views.get_tasks, name='get_tasks'),
    
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
path('add_maintenance_task_page/', views.add_maintenance_task_page, name = "add_maintenance_task_page"),

    path('add_maintenance_task/', views.add_maintenance_task, name = "add_maintenance_task"),
    
    path('maintenance_task/', views.maintenance_task_list, name='maintenance_task_list'),
    path('maintenance_task/edit/<int:id>/', views.edit_maintenance_task, name='edit_maintenance_task'),
    path('maintenance_task/delete/<int:id>/', views.delete_maintenance_task, name='delete_maintenance_task'),
        path('add-tasks/<str:frequency>/', views.add_tasks_for_frequency, name='add_tasks_for_frequency'),

        path('add-task/<str:frequency>/', views.add_task, name='add_task'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
#-----------------------------------------inventory-----------------------------------------------------------

path('requests/', views.issue_list, name='issue_list'),
path('requests/<int:id>/edit/', views.edit_request, name='edit_request'),
path('request/<int:id>/approve/', views.approve_spare_part_request, name='approve_spare_part_request'),
path('request/<int:id>/reject/', views.reject_spare_part_request, name='reject_spare_part_request'),
path('request/<int:id>/issue/', views.issue_spare_part, name='issue_spare_part'),
path('request/<int:id>/cancel/', views.cancel_spare_part_request, name='cancel_spare_part_request'),
# path('request/<int:id>/return/', views.return_spare_part, name='return_spare_part'),
path('request/<int:id>/use/', views.use_spare_part, name='use_spare_part'),
path('request/<int:id>/accept/', views.accept_issued_part, name='accept_issued_part'),


# path('request/<int:id>/accept-return/', views.accept_returned_part, name='accept_returned_part'),
path('request/', views.request_spare_part, name='request_spare_part'),
path('request_page/', views.request_spare_part_page, name='request_spare_part_page'),

#----------------------------------------------returns------------------------------------------------------------
path('return/', views.request_return_page, name='request_return_page'),


path('returns/<int:id>/request/', views.request_part_return, name='request_part_return'),
# path('returns/<int:id>/edit/', views.edit_return, name='edit_return'),
path('returns/<int:id>/accept/', views.accept_return_request, name='accept_return'),
path('returns/<int:id>/complete/', views.complete_return, name='complete_return'),
# path('returns/<int:id>/reject/', views.reject_return_request, name='reject_return'),
#----------------------------------------------------------------------------------------------------------------


    path('dashboard', views.dashboard, name="dashboard"),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('login_events/', views.login_events, name='login_events'),
    path('maintenance_oversight_dashboard' , views.maintenance_oversight_dashboard,name ="maintenance_oversight_dashboard" ),
    path('maintenance_dashboard' , views.maintenance_dashboard,name ="maintenance_dashboard" ),
    path('client_dashboard' , views.client_dashboard,name ="client_dashboard" ),
    path('inventory_dashboard' , views.inventory_dashboard,name ="inventory_dashboard" ),
    
    path('export-maintenance-pdf/', views.export_maintenance_report_pdf, name='export_maintenance_pdf'),
    path('generate_report', views.generate_report,name= 'generate_report'),
    path('api/equipment-maintenance-types/', views.equipment_maintenance_types_api, name='equipment-maintenance-types'),
    path('api/equipment-maintenance-types-MO/', views.equipment_maintenance_types_api_MO, name='equipment-maintenance-types-MO'),


    
    #-----------------------------------------------------------------------------------
 path('accept_maintenance/<int:maintenance_id>/', views.accept_maintenance, name='accept_maintenance'),
    path('complete_maintenance/<int:maintenance_id>/', views.complete_maintenance, name='complete_maintenance'),
    path('approve_maintenance/<int:maintenance_id>/', views.approve_maintenance, name='approve_maintenance'),
    path('reject_maintenance/<int:maintenance_id>/', views.reject_maintenance, name = 'reject_maintenance'),    
    
    #-----------------------------------------------------------------------------------------------------------
    
    path('accept_work_order/<int:work_order_id>/', views.accept_work_order, name='accept_work_order'),
    path('complete_work_order/<int:work_order_id>/', views.complete_work_order, name='complete_work_order'),
    path('approve_work_order/<int:work_order_id>/', views.approve_work_order, name='approve_work_order'),
    path('reject_work_order/<int:work_order_id>/', views.reject_work_order, name = 'reject_work_order'),    
    path('estimate_price/<int:work_order_id>/', views.estimate_price, name='estimate_price'),
    path('confirm_price/<int:work_order_id>/', views.confirm_price, name='confirm_price'),

    #-----------------------------------------------------------------------------------------------------------
    path('mark_notification_as_read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    # path('sse/notifications/', views.sse_notifications, name='sse_notifications'),
    path('notification_stream/', views.notification_stream, name='notification_stream'),

    
    path('maintenance_due/', views.maintenance_due, name='maintenance_due'),  
    
    path('low_spare_part/', views.low_spare_part, name='low_spare_part'),  

     path('restock_list/', views.restock_list, name='restock_list'),
    path('restock_spare_part/', views.restock_spare_part, name='restock_spare_part'),
        path('restock_spare_part_page/', views.restock_spare_part_page, name='restock_spare_part_page'),


#----------------------------------------------------Import Export----------------------------------------------------------------

   path('export/<str:model_name>/', views.export_data, name='export_data'),
    path('import/<str:model_name>/', views.import_data, name='import_data'),


]