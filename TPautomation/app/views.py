from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages

from django.http import HttpRequest
from datetime import datetime

from django.conf import settings
from django.contrib import auth 
from django.shortcuts import redirect

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed

from app.forms import SignUpForm, LogInForm, AccountManagementBasicForm, \
                        AccountManagementEmailForm, AccountManagementPasswordForm, \
                        ForgetPasswordForm, EmailResetPasswordForm, \
                        NoValidationEmailForm
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from axes.models import AccessAttempt
from ipware.ip import get_ip
from django.contrib.auth.decorators import login_required

from django.db.models import Q


def contact(request):
    res_data ={'title':'Contact', 'message':'Your contact page.', 'year':datetime.now().year,}
    return render(request, 'app/contact.html', res_data)

def about(request):
    res_data ={
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    return render(request, 'app/about.html', res_data)

def index(request):
    res_data ={'title':'Home', 'year':datetime.now().year}
    return render(request, 'app/index.html', res_data)

def login(request):
    if request.method == "GET":
        form = LogInForm()
        res_data ={'title':'登入', 'year':datetime.now().year, 'form':form}
        return render(request, 'app/login.html', res_data)
    if request.method == "POST":
        form = LogInForm(request.POST)
        valid_state = form.is_valid()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        ip_address = get_ip(request)
        failures_res = AccessAttempt.objects.filter(username=username, ip_address=ip_address)
        # 有超過一筆資料
        if failures_res.count() > 0:
            failure_res = failures_res[0]
            failure_count = failure_res.failures
            failure_lasttime = failure_res.attempt_time.replace(tzinfo=None)
            # 超過登入次數限制
            if failure_count >= settings.AXES_FAILURE_LIMIT:
                nowtime = datetime.utcnow().replace(tzinfo=None)
                minutes_from_las_attempt = (nowtime - failure_lasttime)
                # 低於15分鐘內重複登入
                if minutes_from_las_attempt < settings.AXES_COOLOFF_TIME:
                    messages.warning(request, '您的帳戶已經被鎖定，請15分鐘後再嘗試。')
                    res_data ={'title':'帳戶鎖定', 'year':datetime.now().year}
                    return render(request, 'app/message.html', res_data)
                else:
                    failure_res.delete()
        
        if valid_state:
            user = authenticate(username=username, password=password)
            user_logged_in.send(sender = User, request = request, user = user)
            auth.login(request, user)
            if failures_res.count() > 0:
                failures_res[0].delete()
            return redirect("/")
        else:
            print(form.cleaned_data.get('username'))
            user_login_failed.send(sender = User, request = request, 
                                    credentials = {'username': form.cleaned_data.get('username')})
            res_data ={'title':'Login', 'year':datetime.now().year, 'form':form}
            return render(request, 'app/login.html', res_data)

@login_required
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

            mail = EmailMessage('MyApp: 啟用您的帳戶', message, to=[email])
            mail.send(fail_silently=False)

            messages.success(request, "請至信箱收取確認郵件以啟用您的帳號。")
            res_data ={
                    'title':'郵件確認',
                    'year':datetime.now().year,
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
        messages.success(request, "感謝您申請帳號，已經登入您的帳號。")
        res_data ={
                'title':'啟用帳戶成功',
                'year':datetime.now().year,
            }
        return render(request, 'app/message.html', res_data)
    else:
        messages.warning(request, "您傳送的連結已失效，如有問題情聯絡本公司。")
        res_data ={
                'title':'連結已失效',
                'year':datetime.now().year,
            }
        return render(request, 'app/message.html', res_data)

@login_required
def management(request, error=None):
    basic_form = AccountManagementBasicForm()
    email_form = AccountManagementEmailForm()
    password_form = AccountManagementPasswordForm()

    user = request.user
    basic_form['first_name'].initial = user.first_name
    basic_form['username'].initial = user.username
    email_form['username'].initial = user.username
    email_form['email'].initial = user.email
    password_form['username'].initial = user.username

    res_data ={
            'title':'帳戶管理',
            'basic_form':basic_form,
            'email_form':email_form,
            'password_form':password_form,
            'year':datetime.now().year
        }
    return render(request, 'app/acc_management.html', res_data)

@login_required
def email_change(request):
    basic_form = AccountManagementBasicForm(request.POST)
    email_form = AccountManagementEmailForm(request.POST)
    password_form = AccountManagementPasswordForm()
    user = request.user
    password_form['username'].initial = user.username
    
    if email_form.is_valid():
        # get data from form
        username = email_form.cleaned_data['username']
        email = email_form.cleaned_data['email']
        user = User.objects.filter(username=username)[0]

        #modify data
        user.email = email
        user.is_active = False
        user.save()
        auth.logout(request)

        # send email
        message = render_to_string('app/acc_active_email.html', {
            'user': user,
            'domain': get_current_site(request).domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'token':account_activation_token.make_token(user),
        })
        mail = EmailMessage('MyApp: 啟用您的帳戶', message, to=[email])
        mail.send(fail_silently=False)

        # redirect to message page
        messages.success(request, "請至更新的信箱收取郵件，以啟用您的帳戶!")
        res_data ={'title':'Email變更提醒'}
        return render(request, 'app/message.html', res_data)
    else:
        res_data ={
                'title':'帳戶管理',
                'basic_form':basic_form,
                'email_form':email_form,
                'password_form':password_form,
                'year':datetime.now().year
            }
        return render(request, 'app/acc_management.html', res_data)

@login_required
def password_change(request):
    basic_form = AccountManagementBasicForm(request.POST)
    email_form = AccountManagementEmailForm()
    password_form = AccountManagementPasswordForm(request.POST)
    user = request.user
    email_form['username'].initial = user.username
    email_form['email'].initial = user.email

    if password_form.is_valid():
        username = password_form.cleaned_data['username']
        user = User.objects.filter(username=username)[0]
        new_password = password_form.cleaned_data['new_password']
        user.set_password(new_password)
        user.save()
        res_data ={'title':'密碼變更成功', 'year':datetime.now().year}
        return render(request, 'app/message.html', res_data)
    else:
        res_data ={
                'title':'帳戶管理',
                'basic_form':basic_form,
                'email_form':email_form,
                'password_form':password_form, 
                'year':datetime.now().year
            }
        return render(request, 'app/acc_management.html', res_data)  
    


def forget_password(request):
    if request.method == "GET":
        form = ForgetPasswordForm()
        res_data ={
                'title':'忘記密碼',
                'form':form, 
                'year':datetime.now().year
            }
        return render(request, 'app/forget_password.html', res_data)  

    if request.method == "POST":
        form = ForgetPasswordForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            user = User.objects.filter(Q(first_name=first_name) | Q(username=username) | Q(email=email))[0]
            email = user.email

            # send email
            message = render_to_string('app/reset_password_email.html', {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token':account_activation_token.make_token(user),
            })

            mail = EmailMessage('MyApp: 重設您的密碼', message, to=[email])
            mail.send(fail_silently=False)

            messages.success(request, "請至信箱收取信件，以重設您的密碼。")
            res_data ={'title':'密碼變更', 'year':datetime.now().year}
            return render(request, 'app/message.html', res_data)

        else:
            res_data ={
                    'title':'忘記密碼',
                    'form':form, 
                    'year':datetime.now().year
                }
            return render(request, 'app/forget_password.html', res_data)  


def email_reset_password(request, uidb64, token):
    if request.method == "GET":
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            auth.login(request, user)
            form = EmailResetPasswordForm()
            form['first_name'].initial = user.first_name
            form['username'].initial = user.username
            form['email'].initial = user.email
            res_data ={'title':'重設密碼', 'year':datetime.now().year, 'form':form,}
            return render(request, 'app/email_reset_password.html', res_data)
        else:
            messages.warning(request, "您傳送的連結已失效，如有問題情聯絡本公司。")
            res_data ={
                    'title':'連結已失效',
                    'year':datetime.now().year,
                }
            return render(request, 'app/message.html', res_data)

    if request.method == "POST":
        form = EmailResetPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password']
            user = User.objects.filter(username=username)[0]
            user.set_password(new_password)
            user.save()
            messages.success(request, "密碼已經重設成功，請妥善保管您的密碼!")
            res_data ={
                    'title':'重設成功',
                    'year':datetime.now().year,
                }
            return render(request, 'app/message.html', res_data)
        else:
            res_data ={'title':'重設密碼', 'year':datetime.now().year, 'form':form,}
            return render(request, 'app/email_reset_password.html', res_data)
    

def no_validation_email(request):
    if request.method == "GET":
        form = NoValidationEmailForm()
        res_data ={
                'title':'重新寄送驗證信',
                'form':form, 
                'year':datetime.now().year
            }
        return render(request, 'app/no_validation_email.html', res_data)  

    if request.method == "POST":
        form = NoValidationEmailForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            user = User.objects.filter(username=username)[0]
            
            if user.email != email:
                user.email = email
                user.save()

            message = render_to_string('app/acc_active_email.html', {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token':account_activation_token.make_token(user),
            })

            mail = EmailMessage('MyApp: 啟用您的帳戶', message, to=[email])
            mail.send(fail_silently=False)

            messages.success(request, "請至信箱收取確認郵件以啟用您的帳號。")
            res_data ={
                    'title':'郵件確認',
                    'year':datetime.now().year,
                }
            return render(request, 'app/message.html', res_data)
        else:
            res_data ={
                    'title':'重新寄送驗證信',
                    'form':form, 
                    'year':datetime.now().year
                }
            return render(request, 'app/no_validation_email.html', res_data)  


