from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    
    # Participant Management
    path('participants/', views.participant_list, name='participant_list'),
    path('participants/add/', views.participant_add, name='participant_add'),
    path('participants/<int:pk>/edit/', views.participant_edit, name='participant_edit'),
    path('participants/<int:pk>/delete/', views.participant_delete, name='participant_delete'),
    path('participants/<int:pk>/block/', views.participant_block, name='participant_block'),
    path('participants/<int:pk>/send-email/', views.participant_send_email, name='participant_send_email'),
    path('participants/send-all-emails/', views.participant_send_all_emails, name='participant_send_all_emails'),
    path('participant-card/<int:pk>/', views.participant_card, name='participant_card'),
    
    # Tryout Management
    path('tryouts/', views.tryout_list, name='tryout_list'),
    path('tryouts/create/', views.tryout_create, name='tryout_create'),
    path('tryouts/<int:pk>/settings/', views.tryout_settings, name='tryout_settings'),
    path('tryouts/<int:pk>/edit/', views.tryout_edit, name='tryout_edit'),
    path('tryouts/<int:pk>/delete/', views.tryout_delete, name='tryout_delete'),
]
