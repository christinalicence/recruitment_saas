from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class TenantSignupForm(forms.Form):
    company_name = forms.CharField(max_length=100)
    subdomain = forms.SlugField(max_length=50)
    admin_email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit("submit", "Sign Up", css_class="btn-primary")
        )


class TenantLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Login"))
        self.helper.add_input(
            Submit("submit", "Login", css_class="btn-primary")
        )
