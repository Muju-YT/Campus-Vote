from django import forms
from django.contrib.auth import password_validation
from django.db import transaction
from .models import User, StudentProfile, Election, Candidate

class StudentRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
        required=True
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        validators=[password_validation.validate_password],
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        required=True
    )
    
    # StudentProfile specific fields
    student_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student ID'}),
        required=True
    )
    department = forms.ChoiceField(
        choices=StudentProfile.DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    year = forms.ChoiceField(
        choices=StudentProfile.YEAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    profile_photo = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'd-none', 'id': 'studentPhoto'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'password']

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if StudentProfile.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("A student with this ID is already registered.")
        return student_id

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email address is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        # 1. Create and save User
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.username = self.cleaned_data["username"]
        user.role = 'student'
        if commit:
            user.save()

            # 2. Create and save corresponding StudentProfile
            student_profile = StudentProfile.objects.create(
                user=user,
                student_id=self.cleaned_data["student_id"],
                department=self.cleaned_data["department"],
                year=self.cleaned_data["year"],
                profile_photo=self.cleaned_data.get("profile_photo"),
                is_approved=False
            )
        
        return user


class StudentProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    class Meta:
        model = StudentProfile
        fields = ['year', 'profile_photo']
        widgets = {
            'year': forms.Select(attrs={'class': 'form-select'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['full_name'].initial = self.instance.user.full_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            profile.user.full_name = self.cleaned_data['full_name']
            profile.user.save()
        return profile


class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['title', 'description', 'start_date', 'end_date', 'banner', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'required': 'true'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'required': 'true'}),
            'banner': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'photo', 'department', 'year', 'position', 'manifesto', 'election']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control', 'required': 'true'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'year': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'manifesto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': 'true'}),
            'election': forms.Select(attrs={'class': 'form-select', 'required': 'true'}),
        }
