from django import forms
from .models import CompanyProfile
from django.core.exceptions import ValidationError

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            'display_name', 
            'logo', 
            'primary_color', 
            'secondary_color', 
            'background_color',
            'template_choice',  
            'hero_title',       
            'hero_text',      
            'hero_image',
            'about_title', 
            'about_content', 
            'team_photo', 
            'jobs_header_text'
        ]
        
        widgets = {
            'primary_color': forms.TextInput(attrs={
                'type': 'color', 
                'class': 'form-control form-control-color'
            }),
            'secondary_color': forms.TextInput(attrs={
                'type': 'color', 
                'class': 'form-control form-control-color'
            }),
            'background_color': forms.TextInput(attrs={
                'type': 'color', 
                'class': 'form-control form-control-color'
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '40',  # Fits nicely in navigation and headers
                'placeholder': 'e.g., TechStaff Recruitment'
            }),
            'hero_title': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '65',  # 8-12 words, ideal for headlines
                'placeholder': 'Your main headline (40-65 characters works best)'
            }),
            'hero_text': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'maxlength': '200',  # 2-3 sentences, readable at a glance
                'placeholder': 'Supporting text - aim for 120-200 characters'
            }),
            'about_title': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '50',
                'placeholder': 'e.g., Our Story, About Us, Who We Are'
            }),
            'about_content': forms.Textarea(attrs={
                'rows': 6,
                'class': 'form-control',
                'maxlength': '600',  # 3-4 short paragraphs, keeps content scannable
                'placeholder': 'Your company story - 400-600 characters is ideal'
            }),
            'jobs_header_text': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'maxlength': '120',  # One impactful sentence
                'placeholder': 'Brief intro to your opportunities'
            }),
        }
        
        labels = {
            'display_name': 'Company Name',
            'hero_title': 'Hero Headline',
            'hero_text': 'Hero Subtext',
            'hero_image': 'Hero Image',
            'about_title': 'About Page Title',
            'about_content': 'About Us Content',
            'team_photo': 'Team Photo',
            'jobs_header_text': 'Jobs Section Intro',
        }
        
        help_texts = {
            'display_name': 'Max 40 characters - appears in navigation',
            'hero_title': '40-65 characters recommended for impact',
            'hero_text': '120-200 characters - keep it concise and compelling',
            'hero_image': 'Recommended: 1200x800px landscape, under 2MB',
            'team_photo': 'Recommended: 1200x800px, under 2MB',
            'about_content': '400-600 characters tells your story without overwhelming',
            'jobs_header_text': 'One sentence intro - max 120 characters',
        }

    def clean_display_name(self):
        """Company name must fit in navigation - 40 chars max."""
        name = self.cleaned_data.get('display_name')
        if name and len(name) > 40:
            raise ValidationError(
                "Company name is too long for navigation. Please shorten to 40 characters or less."
            )
        if name and len(name) < 3:
            raise ValidationError("Company name is too short. At least 3 characters please.")
        return name

    def clean_hero_title(self):
        """Hero title: 40-65 characters is the sweet spot for headlines."""
        title = self.cleaned_data.get('hero_title')
        if title and len(title) > 65:
            raise ValidationError(
                "Hero title is too long. Keep it under 65 characters for best impact. "
                "Currently: {} characters".format(len(title))
            )
        if title and len(title) < 20:
            raise ValidationError(
                "Hero title is too short. Aim for at least 20 characters (about 4-6 words) "
                "for a compelling headline."
            )
        return title

    def clean_hero_text(self):
        """Hero text: 120-200 characters is readable and impactful."""
        text = self.cleaned_data.get('hero_text')
        if text and len(text) > 200:
            raise ValidationError(
                "Hero text is too long ({} chars). Keep it under 200 characters "
                "for better readability.".format(len(text))
            )
        if text and len(text) < 50:
            raise ValidationError(
                "Hero text is too brief. Aim for 120-200 characters (about 2-3 sentences) "
                "to properly support your headline."
            )
        return text

    def clean_about_content(self):
        """About content: 400-600 characters keeps it scannable and engaging."""
        content = self.cleaned_data.get('about_content')
        if content and len(content) > 600:
            raise ValidationError(
                "About content is too long ({} chars). Keep it under 600 characters. "
                "Visitors prefer concise, scannable content.".format(len(content))
            )
        if content and len(content) < 100:
            raise ValidationError(
                "About content is too short. Aim for 400-600 characters "
                "(about 3-4 short paragraphs) to tell your story effectively."
            )
        return content

    def clean_jobs_header_text(self):
        """Jobs header: One sentence, max 120 characters."""
        text = self.cleaned_data.get('jobs_header_text')
        if text and len(text) > 120:
            raise ValidationError(
                "Jobs header is too long. Keep it to one impactful sentence "
                "(max 120 characters)."
            )
        return text

    def clean_hero_image(self):
        image = self.cleaned_data.get('hero_image')
        if image:
            # 10MB limit to be safe for high-res photos
            if image.size > 10 * 1024 * 1024: 
                raise ValidationError("Image is too large. Please keep under 10MB.")
        return image

    def clean_team_photo(self):
        image = self.cleaned_data.get('team_photo')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image is too large. Please keep under 5MB.")
        return image

    def clean_logo(self):
        """Validate logo - smaller size limit for logos."""
        logo = self.cleaned_data.get('logo')
        if logo:
            # Logos should be even smaller - 500KB max
            if logo.size > 500 * 1024:
                raise ValidationError(
                    "Logo is too large ({:.0f}KB). Please keep logos under 500KB.".format(
                        logo.size / 1024
                    )
                )
            
            if not logo.content_type in ['image/jpeg', 'image/jpg', 'image/png', 'image/svg+xml']:
                raise ValidationError("Please upload a JPG, PNG, or SVG logo.")
        
        return logo