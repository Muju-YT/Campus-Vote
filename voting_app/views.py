from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, password_validation
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
import json
from datetime import datetime


from .models import User, StudentProfile, Election, Candidate, Vote, Result
from .forms import StudentRegistrationForm, StudentProfileForm, ElectionForm, CandidateForm

# --- Helper Tests ---
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'admin')

# --- Common / Public Pages ---

def home(request):
    total_students = StudentProfile.objects.filter(is_approved=True).count()
    active_elections = Election.objects.filter(Q(status='Active') | Q(start_date__lte=timezone.now(), end_date__gte=timezone.now())).distinct().count()
    completed_elections = Election.objects.filter(end_date__lt=timezone.now()).count()
    total_votes_cast = Vote.objects.count()

    featured_candidates = Candidate.objects.all()[:3]

    return render(request, 'landing/home.html', {
        'total_students': total_students,
        'active_elections': active_elections,
        'completed_elections': completed_elections,
        'total_votes_cast': total_votes_cast,
        'featured_candidates': featured_candidates,
    })


def about(request):
    return render(request, 'landing/about.html')


def results(request):
    completed_elections = Election.objects.filter(end_date__lt=timezone.now())
    active_elections = Election.objects.filter(Q(status='Active') | Q(start_date__lte=timezone.now(), end_date__gte=timezone.now())).distinct()

    election_results = []
    for election in completed_elections:
        total_votes = Vote.objects.filter(election=election).count()
        candidates = Candidate.objects.filter(election=election).annotate(vote_count=Count('votes')).order_by('-vote_count')
        
        winner = None
        if candidates.exists():
            winner = candidates.first()
            Result.objects.update_or_create(
                election=election,
                defaults={'winner': winner, 'total_votes': total_votes}
            )

        election_results.append({
            'election': election,
            'total_votes': total_votes,
            'candidates': candidates,
            'winner': winner
        })

    return render(request, 'landing/results.html', {
        'election_results': election_results,
        'active_elections': active_elections
    })


# --- Authentication Views ---

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.role == 'admin':
            return redirect('voting_app:admin_dashboard')
        return redirect('voting_app:student_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        if not email or not password:
            messages.error(request, "Please enter both email and password.")
            return render(request, 'auth/login.html')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Check student approval
            if user.role == 'student' and not user.is_superuser:
                try:
                    profile = user.student_profile
                    if not profile.is_approved:
                        messages.error(request, "Your student account is pending admin verification.")
                        return render(request, 'auth/login.html')
                except StudentProfile.DoesNotExist:
                    messages.error(request, "Student profile does not exist. Please contact Admin.")
                    return render(request, 'auth/login.html')

            login(request, user)
            
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)

            # Keep student_id in session for legacy views compatibility
            if user.role == 'student':
                request.session['student_id'] = user.id

            if user.is_superuser or user.role == 'admin':
                messages.success(request, "Admin panel access granted.")
                return redirect('voting_app:admin_dashboard')
            else:
                messages.success(request, f"Welcome, {user.full_name or user.email}!")
                return redirect('voting_app:student_dashboard')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    request.session.flush()
    messages.info(request, "Session terminated successfully.")
    return redirect('voting_app:home')


def register(request):
    if request.user.is_authenticated:
        return redirect('voting_app:student_dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration received! Your student registry account is pending verification.')
            return redirect('voting_app:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = StudentRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})


# --- Student Views ---

@login_required
def student_dashboard(request):
    if request.user.is_superuser or request.user.role == 'admin':
        return redirect('voting_app:admin_dashboard')

    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile missing.")
        logout(request)
        return redirect('voting_app:login')

    today = timezone.now()

    active_elections = Election.objects.filter(
        Q(status='Active') | Q(start_date__lte=today, end_date__gte=today)
    ).distinct()
    completed_count = Election.objects.filter(end_date__lt=today).count()
    votes_cast_count = Vote.objects.filter(student_profile=student).count()

    closest_election = active_elections.order_by('end_date').first()
    election_status = "No active ballots"
    election_progress = 0
    voting_ends_in_days = 0

    if closest_election:
        total_duration = (closest_election.end_date - closest_election.start_date).total_seconds()
        passed_duration = (today - closest_election.start_date).total_seconds()
        if total_duration > 0:
            election_progress = min(100, max(0, int((passed_duration / total_duration) * 100)))
        election_status = f"Polls ending: {election_progress}% completed"
        voting_ends_in_days = (closest_election.end_date - today).days

    all_elections = Election.objects.all().order_by('start_date')

    return render(request, 'student/dashboard.html', {
        'student': student,
        'active_elections': active_elections,
        'completed_count': completed_count,
        'votes_cast_count': votes_cast_count,
        'election_status': election_status,
        'election_progress': election_progress,
        'voting_ends_in_days': voting_ends_in_days,
        'all_elections': all_elections,
    })


@login_required
def vote(request):
    if request.user.is_superuser or request.user.role == 'admin':
        return redirect('voting_app:admin_dashboard')

    student = request.user.student_profile
    today = timezone.now()

    elections = Election.objects.filter(
        Q(status='Active') | Q(start_date__lte=today, end_date__gte=today)
    ).distinct()
    
    # Exclude voted elections
    available_elections = []
    voted_elections_ids = Vote.objects.filter(student_profile=student).values_list('election_id', flat=True)
    
    for el in elections:
        if el.id not in voted_elections_ids:
            available_elections.append(el)

    # AJAX API post handling
    if request.method == 'POST':
        # Accept JSON payloads or POST variables
        if request.content_type == 'application/json' or 'application/json' in request.headers.get('Content-Type', ''):
            try:
                data = json.loads(request.body)
                election_id = data.get('election_id')
                candidate_id = data.get('candidate_id')
            except Exception:
                return JsonResponse({'success': False, 'message': 'Invalid JSON Payload.'}, status=400)
        else:
            election_id = request.POST.get('election_id')
            candidate_id = request.POST.get('candidate_id')

        if not election_id or not candidate_id:
            return JsonResponse({'success': False, 'message': 'Missing ballot parameters.'}, status=400)

        election_obj = get_object_or_404(Election, id=election_id)
        candidate_obj = get_object_or_404(Candidate, id=candidate_id)

        # Respect manual status override to 'Active'
        if election_obj.status != 'Active':
            if election_obj.end_date < today or election_obj.start_date > today:
                return JsonResponse({'success': False, 'message': 'Voting window is closed.'}, status=400)

        # Atomic double-voting check
        try:
            with transaction.atomic():
                already_voted = Vote.objects.select_for_update().filter(student_profile=student, election=election_obj).exists()
                if already_voted:
                    return JsonResponse({'success': False, 'message': 'Ballot already cast in this election.'}, status=400)

                Vote.objects.create(
                    student_profile=student,
                    candidate=candidate_obj,
                    election=election_obj
                )

                student.has_voted = True
                student.save()

                receipt = f"sha256-{student.id}x{candidate_obj.id}e{election_obj.id}"
                return JsonResponse({
                    'success': True, 
                    'message': 'Vote processed successfully!',
                    'receipt': receipt
                })

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Database constraint error.'}, status=500)

    return render(request, 'student/vote.html', {
        'student': student,
        'available_elections': available_elections,
    })


@login_required
def vote_status(request):
    if request.user.is_superuser or request.user.role == 'admin':
        return redirect('voting_app:admin_dashboard')

    student = request.user.student_profile
    votes = Vote.objects.filter(student_profile=student).order_by('-timestamp')
    return render(request, 'student/vote_status.html', {
        'student': student,
        'votes': votes
    })


@login_required
def student_profile(request):
    if request.user.is_superuser or request.user.role == 'admin':
        return redirect('voting_app:admin_dashboard')

    student = request.user.student_profile

    if request.method == 'POST':
        if 'change_password' in request.POST:
            current_pass = request.POST.get('current_password')
            new_pass = request.POST.get('new_password')
            confirm_pass = request.POST.get('confirm_password')

            if not request.user.check_password(current_pass):
                messages.error(request, "Current password verification failed.")
            elif new_pass != confirm_pass:
                messages.error(request, "Confirm password does not match.")
            else:
                try:
                    password_validation.validate_password(new_pass, request.user)
                    request.user.set_password(new_pass)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, "Account credentials updated successfully.")
                except Exception as e:
                    messages.error(request, f"Password rules: {list(e.messages)[0]}")
            return redirect('voting_app:student_profile')

        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student details updated successfully.")
            return redirect('voting_app:student_profile')
        else:
            messages.error(request, "Invalid entries. Verify your details.")
    else:
        form = StudentProfileForm(instance=student)

    votes = Vote.objects.filter(student_profile=student).order_by('-timestamp')

    return render(request, 'student/profile.html', {
        'student': student,
        'form': form,
        'votes': votes
    })


@login_required
def instructions(request):
    student = request.user.student_profile if not request.user.is_superuser and request.user.role != 'admin' else None
    return render(request, 'student/instructions.html', {'student': student})


# --- Admin Dashboard & Core Features ---

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_students = StudentProfile.objects.count()
    approved_students = StudentProfile.objects.filter(is_approved=True).count()
    pending_students = StudentProfile.objects.filter(is_approved=False).count()
    
    total_candidates = Candidate.objects.count()
    total_votes = Vote.objects.count()
    total_elections = Election.objects.count()
    active_elections_count = Election.objects.filter(Q(status='Active') | Q(start_date__lte=timezone.now(), end_date__gte=timezone.now())).distinct().count()

    departments = ['B.Sc CS', 'BCA', 'Commerce', 'Accounting']
    dept_stats = []

    for dept in departments:
        dept_studs = StudentProfile.objects.filter(department=dept).count()
        dept_voted = Vote.objects.filter(student_profile__department=dept).values('student_profile').distinct().count()
        dept_cands = Candidate.objects.filter(department=dept).count()
        
        pct = 0
        if dept_studs > 0:
            pct = round((dept_voted / dept_studs) * 100, 1)

        dept_stats.append({
            'department': dept,
            'total_students': dept_studs,
            'voted': dept_voted,
            'participation': pct,
            'candidates': dept_cands
        })

    active_elections = Election.objects.filter(Q(status='Active') | Q(start_date__lte=timezone.now(), end_date__gte=timezone.now())).distinct().order_by('end_date')
    countdown_text = "N/A"
    countdown_election = "No Active Ballots"
    if active_elections.exists():
        closest_end = active_elections.first().end_date
        time_rem = closest_end - timezone.now()
        hours, remainder = divmod(time_rem.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        countdown_text = f"{time_rem.days}d {hours}h {minutes}m"
        countdown_election = active_elections.first().title

    recent_votes = Vote.objects.all().order_by('-timestamp')[:5]

    return render(request, 'admin/dashboard.html', {
        'total_students': total_students,
        'approved_students': approved_students,
        'pending_students': pending_students,
        'total_candidates': total_candidates,
        'total_votes': total_votes,
        'total_elections': total_elections,
        'active_elections_count': active_elections_count,
        'dept_stats': dept_stats,
        'countdown_text': countdown_text,
        'countdown_election': countdown_election,
        'recent_votes': recent_votes,
    })


@user_passes_test(is_admin)
def admin_students(request):
    approved_students = StudentProfile.objects.filter(is_approved=True)
    pending_students = StudentProfile.objects.filter(is_approved=False)

    if request.method == 'POST':
        if 'add_student' in request.POST:
            form = StudentRegistrationForm(request.POST, request.FILES)
            if form.is_valid():
                user = form.save(commit=False)
                user.save()
                profile = user.student_profile
                profile.is_approved = True
                profile.save()
                messages.success(request, f"Voter account {user.full_name} created and approved.")
                return redirect('voting_app:admin_students')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
        
        elif 'approve_id' in request.POST:
            profile_id = request.POST.get('approve_id')
            profile = get_object_or_404(StudentProfile, id=profile_id)
            profile.is_approved = True
            profile.save()
            messages.success(request, f"Approved registration for {profile.user.full_name}.")
            return redirect('voting_app:admin_students')

        elif 'delete_id' in request.POST:
            profile_id = request.POST.get('delete_id')
            profile = get_object_or_404(StudentProfile, id=profile_id)
            user = profile.user
            profile.delete()
            user.delete()
            messages.success(request, "Voter account purged.")
            return redirect('voting_app:admin_students')

    form = StudentRegistrationForm()
    return render(request, 'admin/students.html', {
        'approved_students': approved_students,
        'pending_students': pending_students,
        'form': form
    })


@user_passes_test(is_admin)
def admin_toggle_approval(request, student_id):
    profile = get_object_or_404(StudentProfile, id=student_id)
    profile.is_approved = not profile.is_approved
    profile.save()
    messages.success(request, f"Approved state toggled for {profile.user.full_name}.")
    return redirect('voting_app:admin_students')


@user_passes_test(is_admin)
def admin_delete_student(request, student_id):
    profile = get_object_or_404(StudentProfile, id=student_id)
    user = profile.user
    profile.delete()
    user.delete()
    messages.success(request, "Student purged from registry.")
    return redirect('voting_app:admin_students')


@user_passes_test(is_admin)
def candidate(request):
    candidates = Candidate.objects.all()
    elections = Election.objects.all()

    if request.method == 'POST':
        if 'add_candidate' in request.POST:
            form = CandidateForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Candidate registered successfully.")
                return redirect('voting_app:candidate')
            else:
                messages.error(request, "Could not enroll candidate. Check fields.")

        elif 'edit_candidate' in request.POST:
            cand_id = request.POST.get('candidate_id')
            cand = get_object_or_404(Candidate, id=cand_id)
            form = CandidateForm(request.POST, request.FILES, instance=cand)
            if form.is_valid():
                form.save()
                messages.success(request, "Candidate information modified.")
                return redirect('voting_app:candidate')
            else:
                messages.error(request, "Verification check failed.")

        elif 'delete_candidate' in request.POST:
            cand_id = request.POST.get('candidate_id')
            cand = get_object_or_404(Candidate, id=cand_id)
            cand.delete()
            messages.success(request, "Candidate removed.")
            return redirect('voting_app:candidate')

    form = CandidateForm()
    return render(request, 'admin/candidate.html', {
        'candidates': candidates,
        'elections': elections,
        'form': form
    })


@user_passes_test(is_admin)
def election(request):
    elections = Election.objects.all().order_by('-start_date')

    if request.method == 'POST':
        if 'add_election' in request.POST:
            form = ElectionForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Election campaign launched!")
                return redirect('voting_app:election')
            else:
                messages.error(request, "Launch parameters invalid.")

        elif 'edit_election' in request.POST:
            elec_id = request.POST.get('election_id')
            elec = get_object_or_404(Election, id=elec_id)
            form = ElectionForm(request.POST, request.FILES, instance=elec)
            if form.is_valid():
                form.save()
                messages.success(request, "Campaign boundaries updated.")
                return redirect('voting_app:election')
            else:
                messages.error(request, "Error saving updates.")

        elif 'delete_election' in request.POST:
            elec_id = request.POST.get('election_id')
            elec = get_object_or_404(Election, id=elec_id)
            elec.delete()
            messages.success(request, "Election purged.")
            return redirect('voting_app:election')

    form = ElectionForm()
    return render(request, 'admin/election.html', {
        'elections': elections,
        'form': form
    })


@user_passes_test(is_admin)
def admin_results(request):
    all_elections = Election.objects.all().order_by('-end_date')
    selected_election_id = request.GET.get('election_id')
    selected_election = None

    if selected_election_id:
        selected_election = get_object_or_404(Election, id=selected_election_id)
    elif all_elections.exists():
        selected_election = all_elections.first()

    candidates_data = []
    total_votes = 0
    winner = None

    if selected_election:
        total_votes = Vote.objects.filter(election=selected_election).count()
        candidates = Candidate.objects.filter(election=selected_election).annotate(vote_count=Count('votes')).order_by('-vote_count')
        
        for cand in candidates:
            pct = 0
            if total_votes > 0:
                pct = round((cand.vote_count / total_votes) * 100, 2)
            
            candidates_data.append({
                'candidate': cand,
                'votes': cand.vote_count,
                'percentage': pct
            })

        if candidates.exists() and total_votes > 0:
            winner = candidates.first()

    return render(request, 'admin/results.html', {
        'all_elections': all_elections,
        'selected_election': selected_election,
        'candidates_data': candidates_data,
        'total_votes': total_votes,
        'winner': winner
    })


@user_passes_test(is_admin)
def settings_page(request):
    if request.method == 'POST':
        messages.success(request, "Global variables configured.")
        return redirect('voting_app:settings')
    return render(request, 'admin/settings.html')
