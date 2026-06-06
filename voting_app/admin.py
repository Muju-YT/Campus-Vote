from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, Election, Candidate, Vote, Result

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'full_name', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('full_name', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('full_name', 'role')}),
    )

class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'department', 'year', 'is_approved', 'has_voted']
    list_filter = ['department', 'year', 'is_approved', 'has_voted']
    search_fields = ['student_id', 'user__email', 'user__full_name']

admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(Election)
admin.site.register(Candidate)
admin.site.register(Vote)
admin.site.register(Result)
