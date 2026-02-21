from django import forms
from .models import CompanyProfile, Job
from django.core.exceptions import ValidationError


# Character limits for key fields to maintain design integrity across themes.
CHAR_LIMITS = {
    'hero_title':          100,
    'hero_text':           300,
    'homepage_body_text':  1200, 
    'about_title':         100,
    'about_content':      1500,
    'jobs_header_text':    250,
}


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            'template_choice', 'display_name', 'logo',
            'primary_color', 'secondary_color', 'background_color',
            'hero_title', 'hero_text', 'hero_image',
            'homepage_body_text',
            'about_title', 'about_content', 'team_photo',
            'jobs_header_text',
            'contact_email', 'contact_phone', 'address',
            'linkedin_url', 'facebook_url',
        ]

        labels = {
            'template_choice':          'Choose Your Site Style',
            'display_name':             'Company Name',
            'hero_title':               'Main Headline',
            'hero_text':                'Hero Sub-text',
            'homepage_body_text':       'Homepage Body Text',
            'jobs_header_text':         'Job Page Heading & Intro',
            'primary_color':            'Hero Background Colour',
            'secondary_color':          'Text & Button Colour',
            'background_color':         'Page Background Colour',
        }

        help_texts = {
            'logo':                     'Max 10MB. Displayed in the navigation bar.',
            'team_photo':               'Max 10MB. Recommended 1200×800px.',
            'hero_image':               'Max 10MB. High resolution recommended.',
            'hero_title':               'Recommended: 40-70 characters for best impact.',
            'hero_text':                'Recommended: 120-200 characters.',
            'homepage_body_text':       'Recommended: 700-850 characters, maximum 1200.',
            'about_title':              'Recommended: 30-60 characters.',
            'about_content':            'Recommended: 600-1000 characters.',
            'jobs_header_text':         'Recommended: 100-180 characters.',
        }

        widgets = {
            'primary_color':     forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'secondary_color':   forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'background_color':  forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'homepage_body_text': forms.Textarea(attrs={'rows': 5, 'data-maxchars': CHAR_LIMITS['homepage_body_text'], 'data-recco-min': 350, 'data-recco-max': 600}),
            'about_content': forms.Textarea(attrs={'rows': 8, 'data-maxchars': CHAR_LIMITS['about_content'], 'data-recco-min': 600, 'data-recco-max': 1000}),
            'address':           forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g. 123 Recruiter Way,\nLondon,\nNW1 1AA'}),
            'jobs_header_text': forms.Textarea(attrs={'rows': 2, 'data-maxchars': CHAR_LIMITS['jobs_header_text'], 'data-recco-min': 100, 'data-recco-max': 180}),
            'hero_title': forms.TextInput(attrs={'data-maxchars': CHAR_LIMITS['hero_title'], 'data-recco-min': 40, 'data-recco-max': 70}),
            'hero_text': forms.Textarea(attrs={'rows': 3, 'data-maxchars': CHAR_LIMITS['hero_text'], 'data-recco-min': 120, 'data-recco-max': 200}),
            'about_title': forms.TextInput(attrs={'data-maxchars': CHAR_LIMITS['about_title'], 'data-recco-min': 30, 'data-recco-max': 60}),
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

        if 'master_application_email' in self.fields:
            self.fields['master_application_email'].required = True

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


class JobApplicationForm(forms.Form):
    full_name = forms.CharField(max_length=100, required=False, label="Full Name")
    email = forms.EmailField(required=False, label="Email Address")
    phone = forms.CharField(max_length=20, required=False, label="Phone Number")
    cv = forms.FileField(required=False, label="Upload CV")