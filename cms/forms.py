from django import forms
from .models import CompanyProfile, Job
from django.core.exceptions import ValidationError

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            'template_choice', 'display_name', 'logo',
            'master_application_email',
            'primary_color', 'secondary_color', 'background_color',
            'hero_title', 'hero_text', 'hero_image',
            'about_title', 'about_content', 'team_photo',
            'jobs_header_text',
            'contact_email', 'contact_phone', 'address',
            'linkedin_url', 'facebook_url',
        ]
        
        labels = {
            'master_application_email': 'Main Email For Job Applications',
            'template_choice': 'Choose Your Site Style',
            'display_name': 'Company Name',
            'hero_title': 'Main Headline',
            'hero_text': 'Introduction Sub-text',
            'jobs_header_text': 'Job Page title and intro text',
        }

        help_texts = {
            'master_application_email': 'Applications will be sent here unless specified otherwise on a specific job post.',
            'logo': 'Max size 10MB. Cloudinary supported.',
            'team_photo': 'Max size 10MB. Recommended 1200x800px.',
            'hero_image': 'Max size 10MB. High resolution recommended.',
        }

        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'hero_text': forms.Textarea(attrs={'rows': 3}),
            'about_content': forms.Textarea(attrs={'rows': 5}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g. 123 Recruiter Way,\nLondon,\nNW1 1AA'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # These fields are allowed to be blank without crashing the form
        optional_fields = [
            'contact_email', 'contact_phone', 'address', 
            'linkedin_url', 'facebook_url', 'secondary_color',
            'jobs_header_text', 'team_photo'
        ]
        for field_name in optional_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

    def clean_about_title(self):
        title = self.cleaned_data.get('about_title')
        if title and len(title) > 100:
            raise ValidationError("About title must be under 100 characters.")
        return title

    def clean_jobs_header_text(self):
        text = self.cleaned_data.get('jobs_header_text')
        if text and len(text) > 150:
            raise ValidationError("Jobs header text must be under 150 characters.")
        return text
    

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'location', 'salary', 'summary', 
            'description', 'custom_recipient_1', 'custom_recipient_2'
        ]

        labels = {
            'custom_recipient_1': 'Recruiter Email 1',
            'custom_recipient_2': 'Recruiter Email 2',
            'summary': 'Short Summary',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'summary': forms.TextInput(attrs={'placeholder': 'A one-sentence pitch for the job card'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'salary': forms.TextInput(attrs={'class': 'form-control'}),
        }