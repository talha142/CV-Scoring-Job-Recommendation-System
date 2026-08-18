# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)  # default avoids migration prompt
    # add more fields later (avatar, bio, etc.)

    def __str__(self):
        return self.user.username

def upload_resume_path(instance, filename):
    return f"resumes/{instance.user.username}_{int(timezone.now().timestamp())}_{filename}"

class UploadedCV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cvs')
    file = models.FileField(upload_to=upload_resume_path)
    parsed_text = models.TextField(blank=True, null=True)
    score = models.IntegerField(default=0)
    top_jobs = models.JSONField(default=list, blank=True)  # store list of top jobs
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"
