from django.db import models
from app.models import Employee

class JobDescription(models.Model):
    title = models.CharField(max_length=255)
    required_skills = models.JSONField()
    nice_to_have_skills = models.JSONField(blank=True)
    required_years_experience = models.FloatField()
    required_degrees = models.JSONField(blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Resume(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='resumes/')
    parsed_data = models.JSONField(null=True, blank=True)
    scores = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume for {self.employee.full_name if self.employee else 'Candidate'}"
