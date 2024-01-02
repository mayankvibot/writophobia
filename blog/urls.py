from django.urls import path, include
from blog.views import (
    BlogSelectedView, 
    HomeView, 
    ProfileView,
    ContactView,
    APICreate
)
from django.views.generic import TemplateView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('view/<str:pk>/', BlogSelectedView.as_view(), name='blog-detail'),
    path('profile/reetika_gautam/', TemplateView.as_view(template_name='custom/reetika.html'), name='reetika_profile'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('my_profile/', ProfileView.as_view(), name='my_profile'),
    path('contact-us/', ContactView.as_view(), name='contact-us'),
    path('api_create/', APICreate.as_view()),
    path('reetika_gautam/', TemplateView.as_view(template_name='custom/reetika.html')),
]
