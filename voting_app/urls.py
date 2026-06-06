from django.urls import path
from . import views

app_name = 'voting_app'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('results/', views.results, name='results'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register,  name='register'),
    

    # Admin
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('students/', views.admin_students, name='admin_students'),
    path('students/toggle/<int:student_id>/', views.admin_toggle_approval, name='admin_toggle_approval'),
    path('students/delete/<int:student_id>/', views.admin_delete_student, name='admin_delete_student'),
    path('candidates/', views.candidate, name='candidate'),
    path('election/', views.election, name='election'),
    path('admin/results/', views.admin_results, name='admin_results'),
    path('settings/', views.settings_page, name='settings'),

    # Student
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/vote/', views.vote, name='vote'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/vote-status/', views.vote_status, name='vote_status'),
    path('student/instructions/', views.instructions, name='instructions'),
]
