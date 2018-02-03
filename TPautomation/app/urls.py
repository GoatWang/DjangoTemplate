from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('login', views.login, name='login'),
    re_path('login/(?P<redirect_to>.+)', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('signup', views.signup, name='signup'),
    re_path('^activate/(?P<uidb64>.+)/(?P<token>.+)/$',views.activate, name="activate"),
]