from django import forms
from . models import Case, County, Constituency,Ward,Location,Sub_Location
from . models import Police_Officer,Police_Station,Response,Suspect,Badge_Number


import re

class SignUpForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'})
    )

    class Meta:
        model = Police_Officer
        fields = ['badge_number','email_address', 'password_hash']
        labels = {
            'badge_number': 'Badge Number',
            'email_address': 'Email Address',
            'password_hash': 'Password',
            'confirm_password': 'Confirm Password',
        }
        widgets = {
            'badge_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Badge Number'}),
            'email_address': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'password_hash': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password_hash")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Password and confirm password do not match")

    def clean_badge_number(self):
        badge_number = self.cleaned_data['badge_number']
        # Define the regular expression pattern for the badge number format
        pattern = re.compile(r'^[A-Z]{3}\d{3}$')
        if not pattern.match(badge_number):
            raise forms.ValidationError("Badge number must start with 3 uppercase letters followed by 3 numbers.")
        return badge_number

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_password(self.cleaned_data["password_hash"])
        if commit:
            instance.save()
        return instance


class LoginForm(forms.Form):
    email_address = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email_address = cleaned_data.get("email_address")
        password = cleaned_data.get("password")
        return cleaned_data
    
    
    
class AnswerForm(forms.ModelForm):
    ob_number = forms.ModelChoiceField(
        queryset=Case.objects.all(),
        required=True,
        label='Case Book Number',
        widget=forms.Select(attrs={'class': 'blue-input-box'}),
    )
    
    class Meta:
        model = Response
        fields = ['ob_number','national_id_no','trace', 'recidivist', 'question1', 'question2', 'question3', 'query1', 'query2', 'query3']
        labels = {
            'ob_number': 'Select the case description',
            'national_id_no': 'Enter the suspect national id number',
            'trace': 'Is there a trace of Suspect in Crime Scene ? ',
            'recidivist': 'Have the Suspect been involved in a similar case before ? ',
            'question1': 'Can you describe what happened on the incident day providing as many details as possible.',
            'question2': 'Can you think of any reason why someone would lie about this incident ? If yes, explain.',
            'question3': 'Are you aware of any other complaints made by the accuser ? If yes, State.',
            'query1': 'Provide detailed description of the incident day events.',
            'query2': 'Any motive for dishonesty about the incident? Please elaborate if applicable.',
            'query3': 'Have you heard of any additional complaints filed by the accuser? If so, specify.',
        }
        widgets = {
            'national_id_no': forms.TextInput(attrs={'class': 'black-input-box'}),
            'trace': forms.Select(choices=[('Yes', 'Yes'), ('No', 'No')], attrs={'class': 'black-input-box'}),
            'recidivist': forms.Select(choices=[('Yes', 'Yes'), ('No', 'No')], attrs={'class': 'black-input-box'}),
            'question1': forms.TextInput(attrs={'class': 'black-input-box'}),
            'question2': forms.TextInput(attrs={'class': 'black-input-box'}),
            'question3': forms.TextInput(attrs={'class': 'black-input-box'}),
            'query1': forms.TextInput(attrs={'class': 'black-input-box'}),
            'query2': forms.TextInput(attrs={'class': 'black-input-box'}),
            'query3': forms.TextInput(attrs={'class': 'black-input-box'}),
        }

class InterrogatorReportForm(forms.Form):
    serial_number = forms.CharField(
        max_length=50,
        help_text = "Enter the 50-alphanumeric serial number",
        widget=forms.TextInput(attrs={'class': 'blue-input-box'})
    )

class PasswordResetForm(forms.Form):
    email_address = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'})
    )
    
    def clean_email_address(self):
        email_address = self.cleaned_data.get('email_address')
        if not Police_Officer.objects.filter(email_address=email_address).exists():
            raise forms.ValidationError("This email address is not associated with any account.")
        return email_address
    
    
class ResetForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'})
    )
    
    class Meta:
        model = Police_Officer
        fields = ['badge_number','email_address', 'password_hash']
        labels = {
            'badge_number': 'Badge Number',
            'email_address': 'Email Address',
            'password_hash': 'Password',
            'confirm_password': 'Confirm Password',
        }
        widgets = {
            'badge_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Badge Number'}),
            'email_address': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'password_hash': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password_hash")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Password and confirm password do not match")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_password(self.cleaned_data["password_hash"])
        if commit:
            instance.save()
        return instance