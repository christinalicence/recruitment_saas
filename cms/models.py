from django.db import models


class Page(models.Model):
    # Basic CMS Page model
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    def __str__(self):
        return self.title


class Job(models.Model):
    # Job Posting model
    title = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150, blank=True, null=True) # Optional
    salary = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    summary = models.CharField(max_length=255, help_text="A one-sentence hook for the job list.")
    description = models.TextField() # Ad description
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.title} - {self.location}"
    