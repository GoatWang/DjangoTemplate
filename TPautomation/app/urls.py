from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    re_path('^activate/(?P<uidb64>.+)/(?P<token>.+)/$',views.activate, name="activate"),
    path('management/',views.management, name="management"),
    path('email_change/',views.email_change, name="email_change"),
    path('password_change/',views.password_change, name="password_change"),
    path('forget_password/',views.forget_password, name="forget_password"),
    re_path('email_reset_password/(?P<uidb64>.+)/(?P<token>.+)/$',views.email_reset_password, name="email_reset_password"),
    path('no_validation_email/',views.no_validation_email, name="no_validation_email"),
]