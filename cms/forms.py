from django import forms
from .models import CompanyProfile

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
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
            'background_color': forms.TextInput(attrs={'type': 'color'}),
        }
        # This changes the text on the screen without changing the database
        labels = {
            'display_name': 'Company Name',
        }
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'hero_text': forms.Textarea(attrs={'rows': 3}),
            'about_content': forms.Textarea(attrs={'rows': 5}),
        }