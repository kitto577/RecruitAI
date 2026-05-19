from django.urls import path
from . import views

urlpatterns = [

    # Authentication
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # HR Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Job CRUD
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/new/', views.job_create, name='job_create'),
    path('jobs/<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='job_delete'),

    # Resume / Candidate
    path('resumes/upload/', views.upload_resume, name='upload_resume'),
    path('resumes/<int:pk>/', views.candidate_detail, name='candidate_detail'),
    path('resumes/<int:pk>/delete/', views.delete_candidate, name='delete_candidate'),
    path('resumes/<int:pk>/status/', views.update_status, name='update_status'),

    # AI Screening
    path('jobs/<int:job_id>/screen/', views.run_screening, name='run_screening'),

    # Candidate Portal
    path('portal/', views.candidate_portal, name='candidate_portal'),
    path('portal/apply/<int:job_id>/', views.apply_for_job, name='apply_for_job'),
    path('portal/my-applications/', views.my_applications, name='my_applications'),
    path('portal/score/<int:cand_id>/', views.view_my_score, name='view_my_score'),

    # Reports
    path('jobs/<int:job_id>/report/', views.download_pdf_report, name='download_report'),

    # APIs
    path('api/chat/', views.chatbot_api, name='chatbot_api'),
    path('api/analytics/<int:job_id>/', views.analytics_api, name='analytics_api'),
]