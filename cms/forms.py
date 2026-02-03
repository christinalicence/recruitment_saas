from django import forms
from .models import CompanyProfile, Job
from django.core.exceptions import ValidationError

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            # Identity
            'template_choice',
            'display_name', 
            'logo',
            
            # Colors
            'primary_color', 
            'secondary_color', 
            'background_color',
            
            # Hero Section
            'hero_title',       
            'hero_text',      
            'hero_image',
            
            # Value Props
            'value_prop_1_title',
            'value_prop_1_text',
            'value_prop_2_title',
            'value_prop_2_text',
            'value_prop_3_title',
            'value_prop_3_text',
            
            # About Page
            'about_title', 
            'about_content', 
            'team_photo',
            
            # Jobs Section
            'jobs_header_text',
            'featured_job',
            
            # Stats (Optional)
            'show_stats',
            'stat_placements',
            'stat_satisfaction',
            'stat_companies',
            'stat_experience',
            
            # Contact & Social
            'contact_email',
            'contact_phone',
            'linkedin_url',
            'twitter_url',
            'facebook_url',
        ]
        
        widgets = {
            # Colors
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            
            # Text Inputs
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '40', 'placeholder': 'e.g., TechStaff Recruitment'}),
            'hero_title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '65', 'placeholder': 'Your main headline (40-65 characters)'}),
            'hero_text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'maxlength': '200', 'placeholder': 'Supporting text - 120-200 characters'}),
            
            # Value Props
            'value_prop_1_title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100', 'placeholder': 'e.g., Expert Matching'}),
            'value_prop_1_text': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'maxlength': '200', 'placeholder': 'Brief description'}),
            'value_prop_2_title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100', 'placeholder': 'e.g., Personal Support'}),
            'value_prop_2_text': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'maxlength': '200', 'placeholder': 'Brief description'}),
            'value_prop_3_title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100', 'placeholder': 'e.g., Fast Results'}),
            'value_prop_3_text': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'maxlength': '200', 'placeholder': 'Brief description'}),
            
            # About
            'about_title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '50', 'placeholder': 'e.g., Our Story'}),
            'about_content': forms.Textarea(attrs={'rows': 6, 'class': 'form-control', 'maxlength': '600', 'placeholder': 'Your company story - 400-600 characters'}),
            'jobs_header_text': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'maxlength': '120', 'placeholder': 'Brief intro'}),
            
            # File Uploads
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'hero_image': forms.FileInput(attrs={'class': 'form-control'}),
            'team_photo': forms.FileInput(attrs={'class': 'form-control'}),
            
            # Featured Job
            'featured_job': forms.Select(attrs={'class': 'form-select'}),
            
            # Stats
            'show_stats': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'stat_placements': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'e.g., 500+'}),
            'stat_satisfaction': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'e.g., 95%'}),
            'stat_companies': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'e.g., 200+'}),
            'stat_experience': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'e.g., 10+'}),
            
            # Contact & Social
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'hello@yourcompany.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+44 20 1234 5678'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/company/yourcompany'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://twitter.com/yourcompany'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://facebook.com/yourcompany'}),
        }
        
        labels = {
            'display_name': 'Company Name',
            'logo': 'Logo',
            'hero_title': 'Hero Headline',
            'hero_text': 'Hero Subtext',
            'hero_image': 'Hero Image',
            'value_prop_1_title': 'Benefit 1 Title',
            'value_prop_1_text': 'Benefit 1 Description',
            'value_prop_2_title': 'Benefit 2 Title',
            'value_prop_2_text': 'Benefit 2 Description',
            'value_prop_3_title': 'Benefit 3 Title',
            'value_prop_3_text': 'Benefit 3 Description',
            'about_title': 'About Page Title',
            'about_content': 'About Us Content',
            'team_photo': 'Team Photo',
            'jobs_header_text': 'Jobs Section Intro',
            'featured_job': 'Featured Job',
            'show_stats': 'Show Stats Section',
            'stat_placements': 'Placements',
            'stat_satisfaction': 'Satisfaction',
            'stat_companies': 'Companies',
            'stat_experience': 'Experience',
            'contact_email': 'Contact Email',
            'contact_phone': 'Phone Number',
            'linkedin_url': 'LinkedIn',
            'twitter_url': 'Twitter/X',
            'facebook_url': 'Facebook',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['featured_job'].queryset = Job.objects.all()
        self.fields['featured_job'].empty_label = "No featured job (hide section)"
        
        # Make optional fields not required
        optional_fields = [
            'stat_placements', 'stat_satisfaction', 'stat_companies', 'stat_experience',
            'contact_email', 'contact_phone', 'linkedin_url', 'twitter_url', 'facebook_url'
        ]
        for field_name in optional_fields:
            self.fields[field_name].required = False

    # Validation methods (keeping them concise)
    def clean_display_name(self):
        name = self.cleaned_data.get('display_name')
        if name and len(name) > 40:
            raise ValidationError("Company name too long. Max 40 characters.")
        if name and len(name) < 3:
            raise ValidationError("Company name too short. Min 3 characters.")
        return name

    def clean_hero_title(self):
        title = self.cleaned_data.get('hero_title')
        if title and len(title) > 65:
            raise ValidationError(f"Hero title too long ({len(title)} chars). Max 65 characters.")
        if title and len(title) < 20:
            raise ValidationError("Hero title too short. Min 20 characters for impact.")
        return title

    def clean_hero_text(self):
        text = self.cleaned_data.get('hero_text')
        if text and len(text) > 200:
            raise ValidationError(f"Hero text too long ({len(text)} chars). Max 200 characters.")
        if text and len(text) < 50:
            raise ValidationError("Hero text too brief. Aim for 120-200 characters.")
        return text

    def clean_about_content(self):
        content = self.cleaned_data.get('about_content')
        if content and len(content) > 600:
            raise ValidationError(f"About content too long ({len(content)} chars). Max 600 characters.")
        if content and len(content) < 100:
            raise ValidationError("About content too short. Aim for 400-600 characters.")
        return content

    def clean_hero_image(self):
        image = self.cleaned_data.get('hero_image')
        if image and image.size > 10 * 1024 * 1024:
            raise ValidationError("Image too large. Max 10MB.")
        return image

    def clean_team_photo(self):
        image = self.cleaned_data.get('team_photo')
        if image and image.size > 5 * 1024 * 1024:
            raise ValidationError("Image too large. Max 5MB.")
        return image

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            if logo.size > 500 * 1024:
                raise ValidationError(f"Logo too large ({logo.size / 1024:.0f}KB). Max 500KB.")
            if logo.content_type not in ['image/jpeg', 'image/jpg', 'image/png', 'image/svg+xml', 'image/webp']:
                raise ValidationError("Upload JPG, PNG, SVG, or WebP only.")
        return logo

    def clean(self):
        cleaned_data = super().clean()
        show_stats = cleaned_data.get('show_stats')
        if show_stats:
            stat_fields = ['stat_placements', 'stat_satisfaction', 'stat_companies', 'stat_experience']
            if not any(cleaned_data.get(field) for field in stat_fields):
                raise ValidationError("If stats enabled, provide at least one stat value.")
        return cleaned_data