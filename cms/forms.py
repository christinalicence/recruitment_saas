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
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'hero_text': forms.Textarea(attrs={'rows': 3}),
            'about_content': forms.Textarea(attrs={'rows': 5}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/yourprofile'}),
            'twitter_url': forms.URLInput(attrs={'placeholder': 'https://twitter.com/yourhandle'}),
            'facebook_url': forms.URLInput(attrs={'placeholder': 'https://facebook.com/yourpage'}),
        }

        help_texts = {
            'linkedin_url': 'Full URL required (e.g., https://www.linkedin.com/...)',
            'twitter_url': 'Full URL required (e.g., https://twitter.com/...)',
            'facebook_url': 'Full URL required (e.g., https://facebook.com/...)',
            'contact_phone': 'Enter your full number here.',
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
        if not logo:
            return logo
        if hasattr(logo, 'content_type'):
            if logo.content_type not in ['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml']:
                raise forms.ValidationError("Please upload a valid image (JPG, PNG, WEBP, or SVG).")
            if logo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("This file is a bit too big! Please keep it under 5MB.")
        return logo

    def clean(self):
        cleaned_data = super().clean()
        show_stats = cleaned_data.get('show_stats')
        if show_stats:
            stat_fields = ['stat_placements', 'stat_satisfaction', 'stat_companies', 'stat_experience']
            if not any(cleaned_data.get(field) for field in stat_fields):
                raise ValidationError("If stats enabled, provide at least one stat value.")
        return cleaned_data