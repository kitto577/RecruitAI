import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from functools import wraps

from .models import JobPosting, Candidate, ChatMessage, UserProfile

logger = logging.getLogger(__name__)


# ── Helper: HR only decorator ────────────────────────────────
def hr_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            if request.user.userprofile.role != 'hr':
                return redirect('candidate_portal')
        except:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── Home ─────────────────────────────────────────────────────
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        profile = request.user.userprofile
        if profile.role == 'hr':
            return redirect('dashboard')
        else:
            return redirect('candidate_portal')
    except Exception as e:
        return redirect('candidate_portal')


# ── Login ────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        try:
            if request.user.userprofile.role == 'hr':
                return redirect('dashboard')
            else:
                return redirect('candidate_portal')
        except:
            return redirect('candidate_portal')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            try:
                if user.userprofile.role == 'hr':
                    return redirect('dashboard')
                else:
                    return redirect('candidate_portal')
            except Exception as e:
                return redirect('candidate_portal')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')


# ── Register ─────────────────────────────────────────────────
def register_view(request):
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        role      = request.POST.get('role', 'candidate')

        # ── Validation ──────────────────────────────────────
        # 1. Username required and length
        if not username:
            messages.error(request, 'Username is required.')
            return render(request, 'registration/register.html')
        if len(username) < 3:
            messages.error(request, 'Username must be at least 3 characters.')
            return render(request, 'registration/register.html')
        if not username.isalnum() and '_' not in username:
            messages.error(request, 'Username can only contain letters, numbers, and underscores.')
            return render(request, 'registration/register.html')

        # 2. Email required
        if not email or '@' not in email:
            messages.error(request, 'A valid email address is required.')
            return render(request, 'registration/register.html')

        # 3. Password required and minimum length
        if not password1:
            messages.error(request, 'Password is required.')
            return render(request, 'registration/register.html')
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'registration/register.html')

        # 4. Strong password validation
        has_upper   = any(c.isupper() for c in password1)
        has_lower   = any(c.islower() for c in password1)
        has_digit   = any(c.isdigit() for c in password1)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?/~`' for c in password1)
        COMMON_PASSWORDS = [
            'password', 'password123', '12345678', '123456789',
            'qwerty123', 'iloveyou', 'admin123', 'letmein',
            'welcome1', 'monkey123', 'dragon123', 'master123',
        ]
        if not has_upper:
            messages.error(request, 'Password must contain at least one uppercase letter (A-Z).')
            return render(request, 'registration/register.html')
        if not has_lower:
            messages.error(request, 'Password must contain at least one lowercase letter (a-z).')
            return render(request, 'registration/register.html')
        if not has_digit:
            messages.error(request, 'Password must contain at least one number (0-9).')
            return render(request, 'registration/register.html')
        if not has_special:
            messages.error(request, 'Password must contain at least one special character (!@#$%^&*).')
            return render(request, 'registration/register.html')
        if password1.lower() in COMMON_PASSWORDS:
            messages.error(request, 'This password is too common. Please choose a stronger password.')
            return render(request, 'registration/register.html')
        if username.lower() in password1.lower():
            messages.error(request, 'Password cannot contain your username.')
            return render(request, 'registration/register.html')

        # 5. Passwords must match
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/register.html')

        # 6. Username must be unique
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
            return render(request, 'registration/register.html')

        # 7. Email must be unique
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'registration/register.html')

        # ── Create user — Django hashes password automatically ──
        user = User.objects.create_user(username=username, email=email, password=password1)
        UserProfile.objects.create(user=user, role=role)
        login(request, user)
        messages.success(request, f'Account created! Welcome, {username}!')
        if role == 'hr':
            return redirect('dashboard')
        return redirect('candidate_portal')

    return render(request, 'registration/register.html')


# ── Logout ───────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')


# ── HR Dashboard ─────────────────────────────────────────────
@hr_required
def dashboard(request):
    jobs = JobPosting.objects.filter(created_by=request.user)
    active_job = None
    candidates = []

    job_id = request.GET.get('job_id')
    if job_id:
        active_job = get_object_or_404(JobPosting, id=job_id, created_by=request.user)
    elif jobs.exists():
        active_job = jobs.first()

    if active_job:
        candidates = list(active_job.candidates.order_by('-final_score'))

    return render(request, 'screener/dashboard.html', {
        'jobs': jobs,
        'active_job': active_job,
        'candidates': candidates,
        'total_jobs': jobs.count(),
        'total_cands': Candidate.objects.filter(job__created_by=request.user).count(),
        'shortlisted': Candidate.objects.filter(job__created_by=request.user, status='shortlisted').count(),
        'score_labels': json.dumps([c.name[:12] for c in candidates]),
        'score_values': json.dumps([c.score_pct for c in candidates]),
    })


# ── Job Views ─────────────────────────────────────────────────
@hr_required
def job_list(request):
    jobs = JobPosting.objects.filter(created_by=request.user)
    return render(request, 'screener/job_list.html', {'jobs': jobs})


@hr_required
def job_create(request):
    if request.method == 'POST':
        title           = request.POST.get('title', '').strip()
        description     = request.POST.get('description', '').strip()
        location        = request.POST.get('location', '').strip()
        job_type        = request.POST.get('job_type', 'fulltime')
        salary_type     = request.POST.get('salary_type', 'undisclosed')
        salary_range    = request.POST.get('salary_range', 'not_disclosed')
        required_skills = request.POST.get('required_skills', '[]')
        optional_skills = request.POST.get('optional_skills', '[]')
        min_experience  = request.POST.get('min_experience', 'any')
        min_education   = request.POST.get('min_education', 'any')
        try:
            min_cgpa = float(request.POST.get('min_cgpa') or 0)
        except:
            min_cgpa = 0.0

        if not title or not description:
            messages.error(request, 'Title and description are required.')
            return render(request, 'screener/job_form.html', {'action': 'Create'})

        job = JobPosting.objects.create(
            title=title, description=description, location=location,
            job_type=job_type, salary_type=salary_type, salary_range=salary_range,
            required_skills=required_skills, optional_skills=optional_skills,
            min_experience=min_experience, min_education=min_education,
            min_cgpa=min_cgpa, created_by=request.user
        )
        messages.success(request, f'Job "{job.title}" created!')
        return redirect('dashboard')
    return render(request, 'screener/job_form.html', {'action': 'Create'})


@hr_required
def job_edit(request, pk):
    job = get_object_or_404(JobPosting, pk=pk, created_by=request.user)
    if request.method == 'POST':
        job.title           = request.POST.get('title', job.title).strip()
        job.description     = request.POST.get('description', job.description).strip()
        job.location        = request.POST.get('location', job.location).strip()
        job.job_type        = request.POST.get('job_type', job.job_type)
        job.salary_type     = request.POST.get('salary_type', job.salary_type)
        job.salary_range    = request.POST.get('salary_range', job.salary_range)
        job.required_skills = request.POST.get('required_skills', job.required_skills)
        job.optional_skills = request.POST.get('optional_skills', job.optional_skills)
        job.min_experience  = request.POST.get('min_experience', job.min_experience)
        job.min_education   = request.POST.get('min_education', job.min_education)
        try:
            job.min_cgpa = float(request.POST.get('min_cgpa') or 0)
        except:
            job.min_cgpa = 0.0
        job.save()
        messages.success(request, 'Job updated!')
        return redirect('job_list')
    return render(request, 'screener/job_form.html', {'job': job, 'action': 'Edit'})


@hr_required
def job_delete(request, pk):
    job = get_object_or_404(JobPosting, pk=pk, created_by=request.user)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted.')
        return redirect('job_list')
    return render(request, 'screener/job_confirm_delete.html', {'job': job})


# ── Resume Upload ─────────────────────────────────────────────
@login_required
def upload_resume(request):
    if request.method == 'POST':
        job_id = request.POST.get('job')
        name = request.POST.get('name')
        email = request.POST.get('email', '')
        resume_file = request.FILES.get('resume_file')

        if not all([job_id, name, resume_file]):
            messages.error(request, 'Job, name and resume file are required.')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

        job = get_object_or_404(JobPosting, pk=job_id)
        candidate = Candidate.objects.create(
            job=job,
            name=name,
            email=email,
            resume_file=resume_file,
            user=request.user,
        )
        messages.success(request, f'Resume uploaded for {name}!')
        try:
            if request.user.userprofile.role == 'hr':
                return redirect(f'/dashboard/?job_id={job.id}')
        except:
            pass
        return redirect('my_applications')
    return redirect('dashboard')


@hr_required
def candidate_detail(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    return render(request, 'screener/candidate_detail.html', {'candidate': candidate})


@hr_required
def delete_candidate(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    job_id = candidate.job.id
    candidate.delete()
    messages.success(request, 'Candidate deleted.')
    return redirect(f'/dashboard/?job_id={job_id}')


@hr_required
def update_status(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        candidate.status = request.POST.get('status', candidate.status)
        candidate.save()
        messages.success(request, f'Status updated to {candidate.status}.')
    return redirect(f'/dashboard/?job_id={candidate.job.id}')


# ── AI Screening ──────────────────────────────────────────────
@hr_required
def run_screening(request, job_id):
    job = get_object_or_404(JobPosting, pk=job_id, created_by=request.user)
    candidates = job.candidates.all()
    count = 0

    # Pre-load BERT model once before the loop
    from .nlp_engine import analyze_resume, get_bert_model
    print("[screening] Pre-loading BERT model...")
    get_bert_model()
    print("[screening] Starting screening loop...")

    for c in candidates:
        try:
            result = analyze_resume(c.resume_file.path, job.description, job=job)

            c.raw_text               = result['raw_text'][:50000]
            c.tfidf_score            = result['tfidf_score']
            c.bert_score             = result['bert_score']
            c.final_score            = result['final_score']
            c.skills                 = result['skills']
            c.required_skills_score  = result.get('required_skills_score', 0.0)
            c.optional_skills_score  = result.get('optional_skills_score', 0.0)
            c.experience_score       = result.get('experience_score', 0.0)
            c.education_score        = result.get('education_score', 0.0)
            c.completeness_score     = result.get('completeness_score', 0.0)
            c.required_skills_matched = result.get('required_skills_matched', 0)
            c.optional_skills_matched = result.get('optional_skills_matched', 0)
            c.auto_rejected          = result.get('auto_rejected', False)
            c.rejection_reason       = result.get('rejection_reason', '')

            # Auto assign status based on score
            if result.get('auto_rejected'):
                c.status = 'auto_rejected'
            elif result['final_score'] >= 0.80:
                c.status = 'shortlisted'
            elif result['final_score'] >= 0.50:
                c.status = 'review'
            else:
                c.status = 'pending'

            c.processed_at = timezone.now()
            c.save()
            count += 1
        except Exception as e:
            logger.error(f'Error screening {c.name}: {e}')
            import traceback
            traceback.print_exc()

    ranked = list(job.candidates.filter(final_score__gt=0).order_by('-final_score'))
    for i, c in enumerate(ranked, 1):
        c.rank = i
        c.save(update_fields=['rank'])

    messages.success(request, f'Screening complete! {count} resumes analyzed.')
    return redirect(f'/dashboard/?job_id={job_id}')


# ── Candidate Portal ──────────────────────────────────────────
@login_required
def candidate_portal(request):
    jobs = JobPosting.objects.filter(is_active=True)
    return render(request, 'screener/candidate_portal.html', {'jobs': jobs})


@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, is_active=True)

    if request.method == 'POST':
        name        = request.POST.get('name', '').strip() or request.user.username
        email       = request.POST.get('email', '').strip() or request.user.email
        resume_file = request.FILES.get('resume_file')

        if not resume_file:
            messages.error(request, 'Please upload a resume file.')
            return render(request, 'screener/apply.html', {'job': job})

        candidate = Candidate.objects.create(
            job         = job,
            user        = request.user,
            name        = name,
            email       = email,
            resume_file = resume_file,
        )

        try:
            from .nlp_engine import analyze_resume
            result = analyze_resume(candidate.resume_file.path, job.description)
            candidate.match_score      = result.get('overall_score', 0)
            candidate.extracted_skills = ', '.join(result.get('skills', []))
            candidate.ai_summary       = result.get('summary', '')
            candidate.save()
        except Exception:
            pass

        messages.success(request, 'Application submitted successfully!')
        return redirect('my_applications')

    return render(request, 'screener/apply.html', {'job': job})


@login_required
def my_applications(request):
    applications = Candidate.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'screener/my_applications.html', {'applications': applications})


@login_required
def view_my_score(request, cand_id):
    candidate = get_object_or_404(Candidate, pk=cand_id, user=request.user)
    return render(request, 'screener/candidate_score.html', {'candidate': candidate})


# ── PDF Report ────────────────────────────────────────────────
@hr_required
def download_pdf_report(request, job_id):
    job = get_object_or_404(JobPosting, pk=job_id, created_by=request.user)
    candidates = list(job.candidates.order_by('-final_score'))
    try:
        from .report_generator import generate_pdf_report
        pdf_bytes = generate_pdf_report(job, candidates, request.user)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Report_{job.title}.pdf"'
        return response
    except Exception as e:
        messages.error(request, f'Report error: {e}')
        return redirect(f'/dashboard/?job_id={job_id}')


# ── Chatbot API ───────────────────────────────────────────────
@login_required
def chatbot_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        job_id = data.get('job_id')
        mode = data.get('mode', 'hr')
        if not message:
            return JsonResponse({'error': 'Empty message'}, status=400)
        job = JobPosting.objects.filter(pk=job_id).first() if job_id else None
        # For candidate mode, find this user's candidate record
        candidate = None
        if mode == 'candidate' and request.user.is_authenticated:
            from .models import Candidate
            candidate = Candidate.objects.filter(user=request.user).order_by('-uploaded_at').first()
        from .chatbot import process_chat
        result = process_chat(message, job=job, candidate=candidate, user=request.user, mode=mode)
        return JsonResponse({'message': result['message'], 'intent': result['intent']})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ── Analytics API ─────────────────────────────────────────────
@hr_required
def analytics_api(request, job_id):
    job = get_object_or_404(JobPosting, pk=job_id, created_by=request.user)
    candidates = list(job.candidates.order_by('-final_score'))
    return JsonResponse({
        'names': [c.name[:15] for c in candidates],
        'final_scores': [c.score_pct for c in candidates],
        'tfidf_scores': [round(c.tfidf_score * 100, 1) for c in candidates],
        'bert_scores': [round(c.bert_score * 100, 1) for c in candidates],
        'statuses': {
            'pending': len([c for c in candidates if c.status == 'pending']),
            'review': len([c for c in candidates if c.status == 'review']),
            'shortlisted': len([c for c in candidates if c.status == 'shortlisted']),
            'rejected': len([c for c in candidates if c.status == 'rejected']),
        }
    })
