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
        # Customizing widgets for better UI in the editor
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'hero_text': forms.Textarea(attrs={'rows': 3}),
            'about_content': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'display_name': 'Company Name',
        }

    def clean_hero_image(self):
        """Validates the hero image upload."""
        image = self.cleaned_data.get('hero_image')
        if image:
            # Check file size (e.g., limit to 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("The hero image is too large. Please keep it under 5MB.")
        return image

    def clean_team_photo(self):
        """Validates the team photo upload."""
        image = self.cleaned_data.get('team_photo')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("The team photo is too large. Please keep it under 5MB.")
        return image