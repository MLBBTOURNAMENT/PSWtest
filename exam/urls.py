from django.urls import path
from . import views

app_name = 'exam'

urlpatterns = [
    path('tryout-list/', views.tryout_list, name='tryout_list'),
    path('tryout/<int:pk>/start/', views.start_tryout, name='start_tryout'),
    path('tryout/<int:pk>/exam/', views.take_exam, name='take_exam'),
    path('tryout/<int:pk>/save-answer/', views.save_answer, name='save_answer'),
    path('tryout/<int:pk>/submit/', views.submit_exam, name='submit_exam'),
    path('tryout/<int:pk>/track-out/', views.track_out_of_app, name='track_out_of_app'),
    path('tryout/<int:pk>/thanks/', views.thank_you, name='thank_you'),
]
