# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import ugettext, ugettext_lazy as _


class AuthForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Login',
                'class': 'form-control',

            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password',
                'class': 'form-control',

            }
        )
    )


class RegForm(UserCreationForm):


    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                    "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")},
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Login',
                'class': 'form-control',

            }
        )
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Email',
                'class': 'form-control',

            }
        ))

    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password',
                'class': 'form-control',

            }
        ))

    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password confirmation',
                'class': 'form-control',

            }
        ),
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ('username', 'email',)

    def clean_email(self):
        self.error_messages.update({
            'duplicate_email': _("A user with that email already exists."),
        })
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )

    def save(self, commit=True):
        user = super(RegForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.save()
        return user
