from django.shortcuts import render
from blog.models import Post, PostViews, Profile, PostLikes
from django.http import HttpResponse
from django.db.models import F
from django.views import View
from blog.filter import PostFilter

from django.shortcuts import  render, redirect
from authenticate.forms import NewUserForm, LoginForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes



def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user_email_exists = Profile.objects.filter(email=request.POST['email'])
			if user_email_exists.exists():
				messages.error(request, "Email already exists, please login to your account")
				return render (request=request, template_name="auth/register.html", context={"register_form":form})
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("home")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="auth/register.html", context={"register_form":form})


from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
	def authenticate(request, form=None, **kwargs):
		email = form.cleaned_data['email']
		password=form.cleaned_data['password']
		UserModel = get_user_model()
		try:
			user = UserModel.objects.get(email=email)
		except UserModel.DoesNotExist:
			return None
		else:
			if user.check_password(password):
				return user
		return None

def login_request(request):
	if request.method == 'GET':
		form = LoginForm()
		return render(request,'auth/login.html', {'form': form})
	elif request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			user = EmailBackend.authenticate(request, form)
			if user:
				login(request, user)
				return redirect(request.GET.get('next', 'home'))
			else:
				messages.error(request,'Username or Password not correct')
				return render(request,'auth/login.html', {'form': form})
        
        # either form not valid or user is not authenticated
		messages.error(request,f'Invalid username or password')
		return render(request,'auth/login.html',{'form': form})
    
def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("main:homepage")



def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "accounts/password/password_reset_email.txt"
					c = {
						"email":user.email,
						'domain':'127.0.0.1:8000',
						'site_name': 'Website',
						"uid": urlsafe_base64_encode(force_bytes(user.pk)),
						"user": user,
						'token': default_token_generator.make_token(user),
						'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("/password_reset/done/")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="accounts/password/password_reset.html", context={"password_reset_form":password_reset_form})