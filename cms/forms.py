from django import forms
from .models import CompanyProfile, Job
from django.core.exceptions import ValidationError


# ─── Character limits (chosen to keep all three themes looking good) ──────────
# hero_title:         60  — fits on one line at all viewport sizes
# hero_text:         160  — two comfortable lines of sub-heading copy
# homepage_body_text: 400 — paragraph beneath the hero image
# about_title:       100  — heading size, should stay short
# about_content:    1200  — generous body copy for the about section
# jobs_header_text:  120  — short intro above the job cards
CHAR_LIMITS = {
    'hero_title':          60,
    'hero_text':          160,
    'homepage_body_text': 400,
    'about_title':        100,
    'about_content':     1200,
    'jobs_header_text':   120,
}


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            'template_choice', 'display_name', 'logo',
            'master_application_email',
            'primary_color', 'secondary_color', 'background_color',
            'hero_title', 'hero_text', 'hero_image',
            'homepage_body_text',
            'about_title', 'about_content', 'team_photo',
            'jobs_header_text',
            'contact_email', 'contact_phone', 'address',
            'linkedin_url', 'facebook_url',
        ]

        labels = {
            'master_application_email': 'Main Email For Job Applications',
            'template_choice':          'Choose Your Site Style',
            'display_name':             'Company Name',
            'hero_title':               'Main Headline',
            'hero_text':                'Hero Sub-text',
            'homepage_body_text':       'Homepage Body Text',
            'jobs_header_text':         'Job Page Heading & Intro',
        }

        help_texts = {
            'master_application_email': 'Applications will be sent here unless a specific job has its own recipient set.',
            'logo':                     'Max 10MB. Displayed in the navigation bar.',
            'team_photo':               'Max 10MB. Recommended 1200×800px.',
            'hero_image':               'Max 10MB. High resolution recommended.',
            'homepage_body_text':       'A short paragraph shown below the hero section on your homepage.',
        }

        widgets = {
            'primary_color':    forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'secondary_color':  forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'hero_text':         forms.Textarea(attrs={'rows': 3,  'data-maxchars': CHAR_LIMITS['hero_text']}),
            'homepage_body_text':forms.Textarea(attrs={'rows': 4,  'data-maxchars': CHAR_LIMITS['homepage_body_text']}),
            'about_content':     forms.Textarea(attrs={'rows': 5,  'data-maxchars': CHAR_LIMITS['about_content']}),
            'address':           forms.Textarea(attrs={'rows': 3,  'placeholder': 'e.g. 123 Recruiter Way,\nLondon,\nNW1 1AA'}),
            'hero_title':        forms.TextInput(attrs={'data-maxchars': CHAR_LIMITS['hero_title']}),
            'about_title':       forms.TextInput(attrs={'data-maxchars': CHAR_LIMITS['about_title']}),
            'jobs_header_text':  forms.Textarea(attrs={'rows': 2,  'data-maxchars': CHAR_LIMITS['jobs_header_text']}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        optional_fields = [
            'contact_email', 'contact_phone', 'address',
            'linkedin_url', 'facebook_url', 'secondary_color',
            'jobs_header_text', 'team_photo', 'homepage_body_text',
        ]
        for field_name in optional_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

    def clean_hero_title(self):
        value = self.cleaned_data.get('hero_title', '')
        if len(value) > CHAR_LIMITS['hero_title']:
            raise ValidationError(f"Keep the headline under {CHAR_LIMITS['hero_title']} characters.")
        return value

    def clean_hero_text(self):
        value = self.cleaned_data.get('hero_text', '')
        if len(value) > CHAR_LIMITS['hero_text']:
            raise ValidationError(f"Keep the hero sub-text under {CHAR_LIMITS['hero_text']} characters.")
        return value

    def clean_homepage_body_text(self):
        value = self.cleaned_data.get('homepage_body_text', '')
        if value and len(value) > CHAR_LIMITS['homepage_body_text']:
            raise ValidationError(f"Homepage body text must be under {CHAR_LIMITS['homepage_body_text']} characters.")
        return value

    def clean_about_title(self):
        value = self.cleaned_data.get('about_title', '')
        if value and len(value) > CHAR_LIMITS['about_title']:
            raise ValidationError(f"About title must be under {CHAR_LIMITS['about_title']} characters.")
        return value

    def clean_jobs_header_text(self):
        value = self.cleaned_data.get('jobs_header_text', '')
        if value and len(value) > CHAR_LIMITS['jobs_header_text']:
            raise ValidationError(f"Jobs header text must be under {CHAR_LIMITS['jobs_header_text']} characters.")
        return value
    

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