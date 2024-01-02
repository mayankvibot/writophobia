from django.urls import path, include
from authenticate.views import register_request, login_request, logout_request

urlpatterns = [
    path('register', register_request, name='register'),
    path("login", login_request, name="login"),
    path("logout", logout_request, name= "logout"),
]
