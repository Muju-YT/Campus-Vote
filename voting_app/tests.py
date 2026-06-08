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
            'username': 'charlie',
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
        self.assertEqual(user.username, 'charlie')
        self.assertEqual(user.email, 'charlie@college.edu')
        self.assertTrue(user.check_password('StrongPassword123!'))

    def test_student_registration_passwords_mismatch(self):
        # Verify passwords mismatch is blocked
        data = {
            'full_name': 'Charlie Brown',
            'username': 'charlie_mismatch',
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
            'username': 'alice_junior',
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


class CampusVoteAuthenticationTests(TestCase):
    def setUp(self):
        # Create student with username different from email
        self.student_user = User.objects.create_user(
            username="john_doe",
            email="john@college.edu",
            password="SecurePassword123!",
            full_name="John Doe",
            role="student"
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            student_id="CS-999",
            department="B.Sc CS",
            year="2nd Year",
            is_approved=True
        )

        # Create admin with username different from email
        self.admin_user = User.objects.create_superuser(
            username="jane_admin",
            email="jane@college.edu",
            password="AdminPassword123!",
            full_name="Jane Admin",
            role="admin"
        )
        self.client = Client()

    def test_student_login_with_email(self):
        # Student logs in with email
        response = self.client.post(reverse('voting_app:login'), {
            'email': 'john@college.edu',
            'password': 'SecurePassword123!'
        })
        # Check redirect to student dashboard
        self.assertRedirects(response, reverse('voting_app:student_dashboard'))

    def test_student_login_with_username(self):
        # Student logs in with username (case insensitive check too)
        response = self.client.post(reverse('voting_app:login'), {
            'email': 'JOHN_DOE',
            'password': 'SecurePassword123!'
        })
        # Check redirect to student dashboard
        self.assertRedirects(response, reverse('voting_app:student_dashboard'))

    def test_admin_login_with_email(self):
        # Admin logs in with email (case insensitive)
        response = self.client.post(reverse('voting_app:login'), {
            'email': 'JANE@college.edu',
            'password': 'AdminPassword123!'
        })
        self.assertRedirects(response, reverse('voting_app:admin_dashboard'))

    def test_admin_login_with_username(self):
        # Admin logs in with username
        response = self.client.post(reverse('voting_app:login'), {
            'email': 'jane_admin',
            'password': 'AdminPassword123!'
        })
        self.assertRedirects(response, reverse('voting_app:admin_dashboard'))

    def test_invalid_login_credentials(self):
        # Login with invalid password
        response = self.client.post(reverse('voting_app:login'), {
            'email': 'john@college.edu',
            'password': 'WrongPassword!'
        })
        self.assertEqual(response.status_code, 200)
        # Check that error message is present
        messages = list(response.context['messages'])
        self.assertTrue(any("Invalid email/username or password." in str(m) for m in messages))

    def test_unapproved_student_login_blocked(self):
        # Create unapproved student
        unapproved_user = User.objects.create_user(
            username="unapproved_student",
            email="unapproved@college.edu",
            password="SecurePassword123!",
            role="student"
        )
        StudentProfile.objects.create(
            user=unapproved_user,
            student_id="CS-888",
            department="B.Sc CS",
            year="1st Year",
            is_approved=False
        )
        # Try to log in with username
        response = self.client.post(reverse('voting_app:login'), {
            'email': 'unapproved_student',
            'password': 'SecurePassword123!'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("pending admin verification" in str(m) for m in messages))


class CampusVoteRegistrationTests(TestCase):
    def setUp(self):
        # Create an existing user and profile to trigger duplicate errors
        self.existing_user = User.objects.create_user(
            username="existing_username",
            email="existing_email@college.edu",
            password="SecurePassword123!",
            role="student"
        )
        self.existing_profile = StudentProfile.objects.create(
            user=self.existing_user,
            student_id="CS-777",
            department="B.Sc CS",
            year="1st Year",
            is_approved=True
        )
        self.client = Client()

    def test_registration_success(self):
        # Test valid student registration
        data = {
            'full_name': 'New Student',
            'username': 'new_voter',
            'email': 'new.voter@college.edu',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
            'student_id': 'CS-666',
            'department': 'B.Sc CS',
            'year': '1st Year'
        }
        response = self.client.post(reverse('voting_app:register'), data)
        self.assertRedirects(response, reverse('voting_app:login'))
        
        # Verify user and profile records created correctly
        user = User.objects.get(username='new_voter')
        self.assertEqual(user.email, 'new.voter@college.edu')
        self.assertEqual(user.full_name, 'New Student')
        self.assertTrue(user.check_password('SecurePassword123!'))
        self.assertEqual(user.role, 'student')
        
        profile = user.student_profile
        self.assertEqual(profile.student_id, 'CS-666')
        self.assertFalse(profile.is_approved)

    def test_registration_duplicate_email(self):
        # Test duplicate email registration failure
        data = {
            'full_name': 'New Student',
            'username': 'unique_user',
            'email': 'existing_email@college.edu', # Collision
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
            'student_id': 'CS-666',
            'department': 'B.Sc CS',
            'year': '1st Year'
        }
        response = self.client.post(reverse('voting_app:register'), data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("email address is already registered" in str(m) for m in messages))

    def test_registration_duplicate_username(self):
        # Test duplicate username registration failure
        data = {
            'full_name': 'New Student',
            'username': 'existing_username', # Collision
            'email': 'unique_email@college.edu',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
            'student_id': 'CS-666',
            'department': 'B.Sc CS',
            'year': '1st Year'
        }
        response = self.client.post(reverse('voting_app:register'), data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("username is already taken" in str(m) for m in messages))

    def test_registration_duplicate_student_id(self):
        # Test duplicate student ID registration failure
        data = {
            'full_name': 'New Student',
            'username': 'unique_user',
            'email': 'unique_email@college.edu',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
            'student_id': 'CS-777', # Collision
            'department': 'B.Sc CS',
            'year': '1st Year'
        }
        response = self.client.post(reverse('voting_app:register'), data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("ID is already registered" in str(m) for m in messages))

    def test_registration_password_mismatch(self):
        # Test password mismatch failure
        data = {
            'full_name': 'New Student',
            'username': 'unique_user',
            'email': 'unique_email@college.edu',
            'password': 'SecurePassword123!',
            'confirm_password': 'DifferentPassword123!',
            'student_id': 'CS-666',
            'department': 'B.Sc CS',
            'year': '1st Year'
        }
        response = self.client.post(reverse('voting_app:register'), data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("Passwords do not match" in str(m) for m in messages))

    def test_registration_invalid_email_format(self):
        # Test invalid email format failure
        data = {
            'full_name': 'New Student',
            'username': 'unique_user',
            'email': 'invalid-email-format',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
            'student_id': 'CS-666',
            'department': 'B.Sc CS',
            'year': '1st Year'
        }
        response = self.client.post(reverse('voting_app:register'), data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("Email" in str(m) or "email" in str(m) for m in messages))


