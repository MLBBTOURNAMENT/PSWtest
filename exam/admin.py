from django.contrib import admin
from .models import ParticipantProfile, Tryout, Question, ParticipantTryout, ParticipantAnswer

@admin.register(ParticipantProfile)
class ParticipantProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'school', 'day', 'blocked']
    list_filter = ['day', 'blocked']
    search_fields = ['full_name', 'school', 'user__username', 'user__email']

@admin.register(Tryout)
class TryoutAdmin(admin.ModelAdmin):
    list_display = ['title', 'publish_time', 'work_time_minutes', 'is_published', 'created_at']
    list_filter = ['is_published', 'publish_time']
    search_fields = ['title', 'description']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['tryout', 'number', 'text']
    list_filter = ['tryout']
    search_fields = ['text']

@admin.register(ParticipantTryout)
class ParticipantTryoutAdmin(admin.ModelAdmin):
    list_display = ['participant', 'tryout', 'started_at', 'finished_at', 'is_finished', 'out_of_app_count']
    list_filter = ['is_finished', 'tryout']
    search_fields = ['participant__full_name']

@admin.register(ParticipantAnswer)
class ParticipantAnswerAdmin(admin.ModelAdmin):
    list_display = ['participant_tryout', 'question', 'selected_option', 'answered_at']
    list_filter = ['selected_option']
