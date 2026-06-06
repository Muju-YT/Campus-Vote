from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import timedelta
import json

from .models import User, StudentProfile, Election, Candidate, Vote
from .forms import StudentRegistrationForm

class CampusVoteSecurityTests(TestCase):
    def setUp(self):
        # Create approved student User and StudentProfile
        self.approved_user = User.objects.create_user(
            username="approved@college.edu",
            email="approved@college.edu",
            password="SecurePassword123!",
            full_name="Approved Student",
            role="student"
        )
        self.approved_profile = StudentProfile.objects.create(
            user=self.approved_user,
            student_id="CS-101",
            department="B.Sc CS",
            year="1st Year",
            is_approved=True
        )

        # Create pending student User and StudentProfile
        self.pending_user = User.objects.create_user(
            username="pending@college.edu",
            email="pending@college.edu",
            password="SecurePassword123!",
            full_name="Pending Student",
            role="student"
        )
        self.pending_profile = StudentProfile.objects.create(
            user=self.pending_user,
            student_id="CS-102",
            department="BCA",
            year="2nd Year",
            is_approved=False
        )

        # Create admin User
        self.admin_user = User.objects.create_superuser(
            username="admin@college.edu",
            email="admin@college.edu",
            password="AdminPassword123!",
            full_name="System Admin",
            role="admin"
        )

        # Create active election
        self.election = Election.objects.create(
            title="Presidential Campaign 2026",
            description="Election for Student President",
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            status="Active"
        )

        # Create candidates
        self.candidate_a = Candidate.objects.create(
            name="Alice Smith",
            department="B.Sc CS",
            position="Student President",
            manifesto="Progress for everyone!",
            election=self.election
        )

        self.candidate_b = Candidate.objects.create(
            name="Bob Jones",
            department="BCA",
            position="Student President",
            manifesto="Building a solid infrastructure.",
            election=self.election
        )

        self.client = Client()

    def test_student_registration_form_valid(self):
        # Verify student registration form validations
        data = {
            'full_name': 'Charlie Brown',
            'student_id': 'CS-103',
            'department': 'Commerce',
            'year': '3rd Year',
            'email': 'charlie@college.edu',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!'
        }
        form = StudentRegistrationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        
        user = form.save()
        self.assertFalse(user.student_profile.is_approved)  # Must start as unapproved
        self.assertEqual(user.username, 'charlie@college.edu')
        self.assertEqual(user.email, 'charlie@college.edu')
        self.assertTrue(user.check_password('StrongPassword123!'))

    def test_student_registration_passwords_mismatch(self):
        # Verify passwords mismatch is blocked
        data = {
            'full_name': 'Charlie Brown',
            'student_id': 'CS-104',
            'department': 'Commerce',
            'year': '3rd Year',
            'email': 'charlie@college.edu',
            'password': 'StrongPassword123!',
            'confirm_password': 'DifferentPassword123!'
        }
        form = StudentRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)

    def test_duplicate_student_id_blocked(self):
        # Verify duplicate student ID is blocked
        data = {
            'full_name': 'Alice Smith Junior',
            'student_id': 'CS-101',  # Matches setUp student_id
            'department': 'B.Sc CS',
            'year': '1st Year',
            'email': 'alice.jr@college.edu',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!'
        }
        form = StudentRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('student_id', form.errors)

    def test_double_voting_prevention_db_constraint(self):
        # Cast first vote
        Vote.objects.create(
            student_profile=self.approved_profile,
            candidate=self.candidate_a,
            election=self.election
        )

        # Attempting to cast second vote in the same election must throw an IntegrityError at DB layer
        with self.assertRaises(IntegrityError):
            Vote.objects.create(
                student_profile=self.approved_profile,
                candidate=self.candidate_b,
                election=self.election
            )

    def test_active_elections_computed_status(self):
        # Validate dynamic status computation logic
        self.assertEqual(self.election.computed_status, "Active")
        
        upcoming_election = Election.objects.create(
            title="Future Vote",
            start_date=timezone.now() + timedelta(days=2),
            end_date=timezone.now() + timedelta(days=4)
        )
        self.assertEqual(upcoming_election.computed_status, "Upcoming")

    def test_ajax_voting_flow(self):
        # Login approved student
        self.client.login(username="approved@college.edu", password="SecurePassword123!")
        
        # Post a vote via AJAX Fetch POST
        response = self.client.post(
            reverse('voting_app:vote'),
            data=json.dumps({
                'election_id': self.election.id,
                'candidate_id': self.candidate_a.id
            }),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.content)
        self.assertTrue(resp_data['success'])
        self.assertIn('receipt', resp_data)
        
        # Try to vote again (double voting check in view)
        response_dup = self.client.post(
            reverse('voting_app:vote'),
            data=json.dumps({
                'election_id': self.election.id,
                'candidate_id': self.candidate_b.id
            }),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response_dup.status_code, 400)
        resp_dup_data = json.loads(response_dup.content)
        self.assertFalse(resp_dup_data['success'])
