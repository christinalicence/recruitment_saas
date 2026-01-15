from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.password_validation import validate_password


class TenantSignupForm(forms.Form):
    company_name = forms.CharField(max_length=100)
    admin_email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput,
        validators=[validate_password],
    )

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
