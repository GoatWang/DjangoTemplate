from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from .models import Report

from django.http import HttpRequest
from datetime import datetime

from django.conf import settings
from django.contrib import auth 
from django.shortcuts import redirect

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from app.forms import SignUpForm, LogInForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    res_data ={
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    return render(request, 'app/contact.html', res_data)

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    res_data ={
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    return render(request, 'app/about.html', res_data)


def index(request):
    assert isinstance(request, HttpRequest)
    try:
        all_reports = Report.objects.all()
        res_data ={
                'title':'Home',
                'year':datetime.now().year,
                'all_reports': all_reports,
            }
    except all_reports.DoesNotExist:
        raise Http404("all_reports does not exist")
    return render(request, 'app/index.html', res_data)

def login(request, redirect_to):
    assert isinstance(request, HttpRequest)
    if request.method == "GET":
        form = LogInForm()
        res_data ={
                'title':'Login',
                'year':datetime.now().year,
                'redirect_to':redirect_to,
                'form':form,
            }
        return render(request, 'app/login.html', res_data)
    if request.method == "POST":
        form = LogInForm(request.POST)
        redirect_to = "/" + redirect_to.split("//")[1]
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(redirect_to)
        else:
            res_data ={
                'title':'Login',
                'year':datetime.now().year,
                'redirect_to':redirect_to,
                'form':form,
            }
            return render(request, 'app/login.html', res_data)

def logout(request):
    auth.logout(request)
    return redirect("/")

def signup(request):
    assert isinstance(request, HttpRequest)
    if request.method == 'GET':
        form = SignUpForm()
        res_data ={
                'title':'註冊',
                'year':datetime.now().year,
                'form':form
            }
        return render(request, 'app/signup.html', res_data)

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            email = form.cleaned_data['email']
            user = User.objects.create_user(username, email, password, first_name=first_name)
            user.is_active = False
            user.save()

            message = render_to_string('app/acc_active_email.html', {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token':account_activation_token.make_token(user),
            })

            send_mail(
                'TP報告產生器: 啟用您的帳戶',
                message,
                '福田稅務諮詢顧問有限公司<jeremy455576@gmail.com>',
                [email],
                fail_silently=False,
            )
            
            res_data ={
                    'title':'郵件確認',
                    'year':datetime.now().year,
                    'message':"請至信箱收取確認郵件以啟用您的帳號。"
                }
            return render(request, 'app/message.html', res_data)
        else:
            res_data ={
                    'title':'註冊',
                    'year':datetime.now().year,
                    'form':form
                }
            return render(request, 'app/signup.html', res_data)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth.login(request, user)
        res_data ={
                'title':'啟用帳戶成功',
                'year':datetime.now().year,
                'message':"感謝您申請帳號，已經登入您的帳號。"
            }
        return render(request, 'app/message.html', res_data)
    else:
        res_data ={
                'title':'啟用帳戶失敗',
                'year':datetime.now().year,
                'message':"您傳送的連結為無效連結，如有問題情聯絡本公司。"
            }
        return render(request, 'app/message.html', res_data)