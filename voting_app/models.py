from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.full_name or self.email


class StudentProfile(models.Model):
    DEPARTMENT_CHOICES = [
        ('B.Sc CS', 'B.Sc CS'),
        ('BCA', 'BCA'),
        ('Commerce', 'Commerce'),
        ('Accounting', 'Accounting'),
    ]

    YEAR_CHOICES = [
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    year = models.CharField(max_length=20, choices=YEAR_CHOICES)
    profile_photo = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    has_voted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name or self.user.email} ({self.student_id})"


class Election(models.Model):
    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    banner = models.ImageField(upload_to='election_banners/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Upcoming')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def computed_status(self):
        if self.status == 'Active':
            return 'Active'
        elif self.status == 'Completed':
            return 'Completed'
        now = timezone.now()
        if now < self.start_date:
            return 'Upcoming'
        elif now > self.end_date:
            return 'Completed'
        else:
            return 'Active'


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='candidate_photos/')
    department = models.CharField(max_length=100)
    year = models.CharField(max_length=20, blank=True, null=True)
    position = models.CharField(max_length=100)
    manifesto = models.TextField()
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.position}"


class Vote(models.Model):
    student_profile = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='votes')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student_profile', 'election')

    def __str__(self):
        return f"{self.student_profile.user.email} voted for {self.candidate.name} in {self.election.title}"


class Result(models.Model):
    election = models.OneToOneField(Election, on_delete=models.CASCADE, related_name='result')
    winner = models.ForeignKey(Candidate, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_results')
    total_votes = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Result for {self.election.title}"
