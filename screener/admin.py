from django.contrib import admin
from .models import UserProfile, JobPosting, Candidate, ChatMessage


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'role']
    list_filter   = ['role']
    search_fields = ['user__username', 'user__email']


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display  = ['title', 'created_by', 'location', 'is_active']
    list_filter   = ['is_active']
    search_fields = ['title', 'description']


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display  = ['name', 'email', 'job', 'final_score', 'rank', 'status', 'uploaded_at']
    list_filter   = ['status', 'job']
    search_fields = ['name', 'email']
    ordering      = ['-final_score']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display  = ['user', 'role', 'intent', 'timestamp']
    list_filter   = ['role', 'intent']
    ordering      = ['-timestamp']
