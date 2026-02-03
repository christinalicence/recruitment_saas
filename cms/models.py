from django.db import models
from django.conf import settings

class CompanyProfile(models.Model):
    TEMPLATE_CHOICES = [
        ('executive', 'The Executive'),
        ('startup', 'The Startup'),
        ('boutique', 'The Boutique'),
    ]
    template_choice = models.CharField(
        max_length=20, 
        choices=TEMPLATE_CHOICES, 
        default='executive'
    )
    display_name = models.CharField(max_length=255) 
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default="#007bff")
    secondary_color = models.CharField(max_length=7, default="#6c757d")
    background_color = models.CharField(max_length=7, default="#ffffff")
    
    # Page 1: Landing Page (Hero Section)
    hero_title = models.CharField(max_length=200, default="Great Careers Await")
    hero_text = models.TextField(blank=True, help_text="The main pitch to candidates")
    hero_image = models.ImageField(upload_to='hero/', null=True, blank=True)
    
    # Page 2: About Us
    about_title = models.CharField(max_length=200, default="Our Story", blank=True, null=True)
    team_photo = models.ImageField(upload_to='team/', null=True, blank=True)
    about_content = models.TextField(blank=True)
    
    # Page 3: Jobs Page
    jobs_header_text = models.TextField(blank=True, default="Explore our current openings.")

    
    def get_hero_image(self):
        """Returns the uploaded hero image URL or a local default based on template."""
        if self.hero_image:
            return self.hero_image.url
        
        return f"{settings.MEDIA_URL}hero/default_{self.template_choice}.jpg"

    def get_team_photo(self):
        """Returns the uploaded team photo URL or the local default."""
        if self.team_photo:
            return self.team_photo.url
        
        # Matches: media/team/default_team.jpg
        return f"{settings.MEDIA_URL}team/default_team.jpg"

    def __str__(self):
        return self.display_name

class Page(models.Model):
    # Basic CMS Page model
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    def __str__(self):
        return self.title

class Job(models.Model):
    # Job Posting model
    title = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150, blank=True, null=True)
    salary = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    summary = models.CharField(max_length=255, help_text="A one-sentence hook for the job list.")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.location}"