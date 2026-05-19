from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('hr', 'HR / Recruiter'),
        ('candidate', 'Job Candidate'),
    ]
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')
    phone      = models.CharField(max_length=20, blank=True)
    bio        = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_hr(self):
        return self.role == 'hr'

    @property
    def is_candidate(self):
        return self.role == 'candidate'


class JobPosting(models.Model):

    # ── Job Type ──────────────────────────────────────────────
    JOB_TYPE_CHOICES = [
        ('fulltime',   'Full Time'),
        ('parttime',   'Part Time'),
        ('internship', 'Internship'),
        ('remote',     'Remote'),
        ('hybrid',     'Hybrid'),
    ]

    # ── Minimum Experience ────────────────────────────────────
    EXPERIENCE_CHOICES = [
        ('any',      'Any / Not Required'),
        ('fresher',  'Fresher Only'),
        ('1',        '1+ Year'),
        ('2',        '2+ Years'),
        ('3',        '3+ Years'),
        ('5',        '5+ Years'),
        ('8',        '8+ Years'),
    ]

    # ── Minimum Education ─────────────────────────────────────
    EDUCATION_CHOICES = [
        ('any',      'Any Degree'),
        ('10th',     '10th Pass'),
        ('12th',     '12th Pass'),
        ('diploma',  'Diploma'),
        ('bca',      'BCA / B.Sc'),
        ('btech',    'B.Tech / B.E.'),
        ('mca',      'MCA / M.Sc'),
        ('mtech',    'M.Tech / M.E.'),
        ('mba',      'MBA'),
        ('phd',      'PhD'),
    ]

    # ── Salary Type ───────────────────────────────────────────
    SALARY_TYPE_CHOICES = [
        ('annual',  'Annual Package (LPA)'),
        ('monthly', 'Monthly Salary'),
        ('stipend', 'Stipend (Internship)'),
        ('undisclosed', 'Not Disclosed'),
    ]

    # ── Annual Salary Ranges ──────────────────────────────────
    ANNUAL_SALARY_CHOICES = [
        ('not_disclosed', 'Not Disclosed'),
        ('below_3',       'Below 3 LPA'),
        ('3_5',           '3 - 5 LPA'),
        ('5_8',           '5 - 8 LPA'),
        ('8_12',          '8 - 12 LPA'),
        ('12_18',         '12 - 18 LPA'),
        ('18_25',         '18 - 25 LPA'),
        ('25_40',         '25 - 40 LPA'),
        ('40_plus',       '40 LPA+'),
    ]

    # ── Monthly Salary Ranges ─────────────────────────────────
    MONTHLY_SALARY_CHOICES = [
        ('not_disclosed', 'Not Disclosed'),
        ('below_15k',     'Below ₹15,000'),
        ('15_25k',        '₹15,000 - ₹25,000'),
        ('25_40k',        '₹25,000 - ₹40,000'),
        ('40_60k',        '₹40,000 - ₹60,000'),
        ('60_100k',       '₹60,000 - ₹1,00,000'),
        ('100k_plus',     '₹1,00,000+'),
    ]

    # ── Stipend Ranges ────────────────────────────────────────
    STIPEND_CHOICES = [
        ('unpaid',    'Unpaid / Certificate Only'),
        ('below_5k',  'Below ₹5,000/month'),
        ('5_10k',     '₹5,000 - ₹10,000/month'),
        ('10_15k',    '₹10,000 - ₹15,000/month'),
        ('15_20k',    '₹15,000 - ₹20,000/month'),
        ('20k_plus',  '₹20,000+/month'),
    ]

    # ── Core fields ───────────────────────────────────────────
    title        = models.CharField(max_length=200)
    description  = models.TextField()
    created_by   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_postings')
    created_at   = models.DateTimeField(default=timezone.now)
    is_active    = models.BooleanField(default=True)
    location     = models.CharField(max_length=200, blank=True)

    # ── New structured fields ─────────────────────────────────
    job_type         = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='fulltime')
    required_skills  = models.TextField(default='[]')   # JSON list
    optional_skills  = models.TextField(default='[]')   # JSON list
    min_experience   = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='any')
    min_education    = models.CharField(max_length=20, choices=EDUCATION_CHOICES, default='any')
    min_cgpa         = models.FloatField(default=0.0)   # 0.0 = no cutoff
    salary_type      = models.CharField(max_length=20, choices=SALARY_TYPE_CHOICES, default='undisclosed')
    salary_range     = models.CharField(max_length=50, default='not_disclosed')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def candidate_count(self):
        return self.candidates.count()

    # ── Skill helpers ─────────────────────────────────────────
    @property
    def required_skills_list(self):
        try:
            return json.loads(self.required_skills)
        except:
            return []

    @required_skills_list.setter
    def required_skills_list(self, value):
        self.required_skills = json.dumps(value)

    @property
    def optional_skills_list(self):
        try:
            return json.loads(self.optional_skills)
        except:
            return []

    @optional_skills_list.setter
    def optional_skills_list(self, value):
        self.optional_skills = json.dumps(value)

    @property
    def min_experience_display(self):
        mapping = {
            'any': 'Any', 'fresher': 'Fresher',
            '1': '1+ Year', '2': '2+ Years',
            '3': '3+ Years', '5': '5+ Years', '8': '8+ Years',
        }
        return mapping.get(self.min_experience, 'Any')

    @property
    def salary_display(self):
        if self.salary_type == 'undisclosed':
            return 'Not Disclosed'
        return self.salary_range.replace('_', ' ').title()


class Candidate(models.Model):
    STATUS_CHOICES = [
        ('pending',       'Pending'),
        ('review',        'Under Review'),
        ('shortlisted',   'Shortlisted'),
        ('rejected',      'Rejected'),
        ('auto_rejected', 'Auto Rejected'),
    ]

    # ── Core fields ───────────────────────────────────────────
    job         = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='candidates')
    user        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    name        = models.CharField(max_length=200)
    email       = models.EmailField(blank=True)
    phone       = models.CharField(max_length=20, blank=True)
    resume_file = models.FileField(upload_to='resumes/')
    raw_text    = models.TextField(blank=True)

    # ── AI Scores ─────────────────────────────────────────────
    tfidf_score  = models.FloatField(default=0.0)
    bert_score   = models.FloatField(default=0.0)
    final_score  = models.FloatField(default=0.0)
    rank         = models.IntegerField(default=0)

    # ── Detailed score breakdown ──────────────────────────────
    required_skills_score  = models.FloatField(default=0.0)
    optional_skills_score  = models.FloatField(default=0.0)
    experience_score       = models.FloatField(default=0.0)
    education_score        = models.FloatField(default=0.0)
    completeness_score     = models.FloatField(default=0.0)

    # ── Skills ────────────────────────────────────────────────
    skills_json              = models.TextField(default='[]')
    required_skills_matched  = models.IntegerField(default=0)
    optional_skills_matched  = models.IntegerField(default=0)

    # ── Auto rejection ────────────────────────────────────────
    auto_rejected     = models.BooleanField(default=False)
    rejection_reason  = models.CharField(max_length=500, blank=True)

    # ── Status & timestamps ───────────────────────────────────
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    uploaded_at  = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-final_score']

    def __str__(self):
        return f"{self.name} - {self.score_pct}%"

    # ── Skills property ───────────────────────────────────────
    @property
    def skills(self):
        try:
            return json.loads(self.skills_json)
        except:
            return []

    @skills.setter
    def skills(self, value):
        self.skills_json = json.dumps(value)

    # ── Score percentage properties ───────────────────────────
    @property
    def score_pct(self):
        return round(self.final_score * 100, 1)

    @property
    def tfidf_pct(self):
        return round(self.tfidf_score * 100, 1)

    @property
    def bert_pct(self):
        return round(self.bert_score * 100, 1)

    @property
    def required_skills_pct(self):
        return round(self.required_skills_score * 100, 1)

    @property
    def optional_skills_pct(self):
        return round(self.optional_skills_score * 100, 1)

    @property
    def experience_pct(self):
        return round(self.experience_score * 100, 1)

    @property
    def education_pct(self):
        return round(self.education_score * 100, 1)

    # ── Missing skills ────────────────────────────────────────
    @property
    def missing_skills(self):
        try:
            from .nlp_engine import extract_skills
            job_skills = extract_skills(self.job.description)
            my_skills  = [s.lower() for s in self.skills]
            return [s for s in job_skills if s.lower() not in my_skills]
        except:
            return []

    @property
    def missing_required_skills(self):
        try:
            required = self.job.required_skills_list
            my_skills = [s.lower() for s in self.skills]
            return [s for s in required if s.lower() not in my_skills]
        except:
            return []

    @property
    def score_label(self):
        if self.auto_rejected:
            return 'Auto Rejected'
        elif self.score_pct >= 80:
            return 'Excellent'
        elif self.score_pct >= 65:
            return 'Good'
        elif self.score_pct >= 50:
            return 'Average'
        elif self.score_pct >= 35:
            return 'Below Average'
        else:
            return 'Poor Match'


class ChatMessage(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('bot', 'Bot')]
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    job       = models.ForeignKey(JobPosting, on_delete=models.SET_NULL, null=True, blank=True)
    role      = models.CharField(max_length=10, choices=ROLE_CHOICES)
    message   = models.TextField()
    intent    = models.CharField(max_length=50, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.role}] {self.message[:50]}"
