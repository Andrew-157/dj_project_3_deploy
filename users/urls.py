from django.views.generic import TemplateView
from django.urls import path
from users import views

app_name = 'users'
urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout', views.logout_request, name='logout'),
    path('user/change/', views.ChangeUserView.as_view(), name='change-user'),
    path('become_user/',
         TemplateView.as_view(template_name='users/become_user.html'),
         name='become-user')
]
