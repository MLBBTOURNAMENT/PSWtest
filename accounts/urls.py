from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.participant_login, name='login'),
    path('logout/', views.participant_logout, name='logout'),
]
