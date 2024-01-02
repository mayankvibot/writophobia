from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from blog.models import Profile
from django.contrib.auth.password_validation import password_validators_help_texts

class NewUserForm(UserCreationForm):
	first_name = forms.CharField(
		label="Enter your First Name", strip=True, widget=forms.TextInput, required=True
	)
	last_name = forms.CharField(
		label="Enter your Last Name", strip=True, widget=forms.TextInput, required=False
	)
	email = forms.CharField(
		label="Enter your Email", strip=True, widget=forms.EmailInput, required=True
	)
	password1 = forms.CharField(
		label="Enter Password", strip=False, widget=forms.PasswordInput
	)
	password2 = None

	class Meta:
		model=Profile
		fields = ["first_name", "last_name", 'email','password1', ] 

	def __init__(self, *args, **kwargs):
		super(NewUserForm, self).__init__(*args, **kwargs)
		self.fields['password1'].required = True
		self.fields['password1'].widget.attrs['autocomplete'] = 'off'

	def get_unique_username(self, profile):
		org_username = profile.email.split("@")[0]
		username = org_username
		count = 0
		while True:
			if count:
				username = f'{org_username}_{count}'
			if not Profile.objects.filter(username=username).exists():
				break
			count+= 1
		return username

	def save(self, commit=True):
		profile = super(NewUserForm, self).save(commit=False)
		profile.email = self.cleaned_data['email']
		profile.username = self.get_unique_username(profile)
		if commit:
			profile.save()
		return profile


class LoginForm(forms.Form):
	email = forms.CharField(max_length=65, required=True)
	password = forms.CharField(max_length=65, widget=forms.PasswordInput, required=True)
