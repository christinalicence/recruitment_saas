from django import forms


class TenantSignupForm(forms.Form):
    company_name = forms.CharField(max_length=100)
    subdomain = forms.SlugField(max_length=50)
    admin_email = forms.EmailField()