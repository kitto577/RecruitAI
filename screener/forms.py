from django import forms
from django.contrib.auth.models import User
from .models import JobPosting, Candidate


class RegisterForm(forms.Form):
    username  = forms.CharField(max_length=150)
    email     = forms.EmailField(required=False)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    role      = forms.ChoiceField(choices=[('candidate','Candidate'),('hr','HR')])

    def clean_username(self):
        u = self.cleaned_data['username']
        if User.objects.filter(username=u).exists():
            raise forms.ValidationError("Username already taken.")
        return u

    def clean(self):
        d = super().clean()
        if d.get('password1') != d.get('password2'):
            raise forms.ValidationError("Passwords do not match.")
        return d


class JobPostingForm(forms.ModelForm):
    class Meta:
        model  = JobPosting
        fields = ['title', 'description', 'location', 'salary_range']


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model  = Candidate
        fields = ['name', 'email', 'resume_file', 'job']
