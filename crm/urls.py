from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import upload_clients

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    #path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('logout/', views.custom_logout_view, name='logout'),
    #path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('clients/', views.client_list, name='client_list'),
    path('clients/<int:client_id>/add_meeting/', views.add_meeting, name='add_meeting'),
    path('clients/<int:client_id>/add_sales/', views.add_sale, name='add_sales'),
    path('clients/update/<int:client_id>/', views.update_client, name='update_client'),
   # path('clients/<int:client_id>/add_sa/', views.add_meeting, name='add_meeting'),
    path('upload-clients/', upload_clients, name='upload_clients'),
    path('success/', views.success_page, name='success_page'),
    #path('schedule-meeting/', views.schedule_meeting, name='schedule_meeting'),
    path('meetings/', views.meetings_list, name='meetings_list'),
    path('meetings/<int:client_id>/', views.meetings_list, name='meetings_list'),
    #path('addsales/<int:client_id>/', views.add_sale, name='add_sale'),
    path('meetings/<int:client_id>/add/', views.add_meeting, name='add_meeting'),
    path('meetings/<int:meeting_id>/update/', views.update_meeting, name='update_meeting'),
    path('meetings/<int:meeting_id>/delete/', views.delete_meeting, name='delete_meeting'),
    path('sales/', views.sales_list, name='sales_list'),
    path('add-client/', views.add_client, name='add_client'),
    path('export-meetings/', views.export_meetings_to_excel, name='export_meetings'),
    path('export-sales/', views.export_sales_to_excel, name='export_sales'),

]




