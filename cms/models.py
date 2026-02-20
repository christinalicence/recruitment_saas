from django.db import models
from django.conf import settings
from django.templatetags.static import static


class CompanyProfile(models.Model):
    tenant_slug = models.CharField(max_length=63, unique=True, editable=False, null=True)
    TEMPLATE_CHOICES = [
        ('executive', 'The Executive'),
        ('startup', 'The Startup'),
        ('boutique', 'The Boutique'),
    ]
    
    # Identity & Branding
    template_choice = models.CharField(
        max_length=20, 
        choices=TEMPLATE_CHOICES, 
        default='executive')
    
    display_name = models.CharField(max_length=255) 
    logo = models.ImageField(
        upload_to='logos/', 
        null=True, 
        blank=True,
        help_text="Your logo (appears in navigation bar)"
    )
    primary_color = models.CharField(max_length=7, default="#0f172a")
    secondary_color = models.CharField(max_length=7, default="#0f172a")
    background_color = models.CharField(max_length=7, default="#ffffff")
    
    # Hero Section
    hero_title = models.CharField(max_length=200, default="Great Careers Await")
    hero_text = models.TextField(blank=True, help_text="The main pitch to candidates")
    hero_image = models.ImageField(upload_to='hero/', null=True, blank=True)
    homepage_body_text = models.TextField(
    blank=True,
    help_text="Short paragraph shown below the hero section on the homepage."
)
    
    # About Us
    about_title = models.CharField(max_length=200, default="Our Story", blank=True)
    team_photo = models.ImageField(upload_to='team/', null=True, blank=True)
    about_content = models.TextField(blank=True)
    
    # Jobs Section
    jobs_header_text = models.TextField(blank=True, default="Explore our current openings.")
    featured_job = models.ForeignKey(
        'Job',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_in_profile',
        help_text="Choose a job to feature on your homepage"
    )
    
    # Contact & Social
    contact_email = models.EmailField(max_length=200, blank=True, help_text="General enquiries email")
    contact_phone = models.CharField(max_length=50, blank=True, help_text="Main contact number")
    address = models.TextField(blank=True, help_text="Full office address for the footer")
    linkedin_url = models.URLField(max_length=200, blank=True)
    facebook_url = models.URLField(max_length=200, blank=True)

    def get_hero_image(self):
        """Returns uploaded hero or the specific default for the chosen theme."""
        if self.hero_image:
            return self.hero_image.url
        filename = f'marketing/images/default_{self.template_choice}.jpg'
        return static(filename)

    def get_team_photo(self):
        """Returns uploaded team photo or the default about image."""
        if self.team_photo:
            return self.team_photo.url
        return static('marketing/images/default_about.jpg')

    def __str__(self):
        return self.display_name


class Job(models.Model):
    title = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150, blank=True, null=True)
    salary = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    summary = models.CharField(
        max_length=255, 
        help_text="A one-sentence hook - shows on homepage if featured"
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    custom_recipient_1 = models.EmailField(
        null=True, 
        blank=True, 
        help_text="Optional: Send applications for this job here instead of the master email."
    )
    custom_recipient_2 = models.EmailField(
        null=True, 
        blank=True, 
        help_text="Optional: A second email to receive applications for this job."
    )
    
    # For future LinkedIn sharing
    linkedin_post_id = models.CharField(max_length=100, blank=True, null=True)
    last_shared_date = models.DateTimeField(null=True, blank=True)
    
    tenant = models.ForeignKey(
        'customers.Client', 
        on_delete=models.CASCADE, 
        related_name='jobs',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.location}"


class Page(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.title