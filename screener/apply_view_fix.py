# ─────────────────────────────────────────────────────────────
# FIND this function in your screener/views.py and REPLACE it
# with the version below
# ─────────────────────────────────────────────────────────────

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

        # Save candidate record
        candidate = Candidate.objects.create(
            job         = job,
            user        = request.user,
            name        = name,
            email       = email,
            resume_file = resume_file,
        )

        # Run AI scoring immediately
        try:
            from .nlp_engine import analyze_resume
            result = analyze_resume(candidate.resume_file.path, job.description)
            candidate.match_score    = result.get('overall_score', 0)
            candidate.extracted_skills = ', '.join(result.get('skills', []))
            candidate.ai_summary     = result.get('summary', '')
            candidate.save()
        except Exception as e:
            pass  # Score will show as 0 if NLP fails — not a blocker

        messages.success(request, f'Application submitted! Your AI match score will appear shortly.')
        return redirect('my_applications')

    # GET request — show the form
    return render(request, 'screener/apply.html', {'job': job})
