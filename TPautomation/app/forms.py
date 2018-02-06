from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q


class SignUpForm(forms.Form):
    first_name = forms.CharField(label='用戶名稱')
    username = forms.CharField(label='帳號')
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, label='密碼')
    password_check = forms.CharField(widget=forms.PasswordInput, label='密碼確認')

    def clean(self):
        super().clean()
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        first_name = self.cleaned_data.get('first_name')
        password = self.cleaned_data.get('password')
        password_check = self.cleaned_data.get('password_check')

        username_count = User.objects.filter(username=username).count()
        if username_count>0:
            raise forms.ValidationError("此帳號已經有人使用!")
        email_count = User.objects.filter(email=email).count()
        if email_count>0:
            raise forms.ValidationError("此信箱已經註冊!")
        first_name_count = User.objects.filter(first_name=first_name).count()
        if first_name_count>0:
            raise forms.ValidationError("此用戶名稱已經註冊!")
        if password != password_check:
            raise forms.ValidationError("輸入密碼與確認密碼不一致!")

        try:
            validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError(e)

class LogInForm(forms.Form):
    username = forms.CharField(label='帳號')
    password = forms.CharField(widget=forms.PasswordInput, label='密碼')
    
    def clean(self):
        super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = User.objects.filter(username=username)[0]
        if not user.is_active:
            raise forms.ValidationError("請至信箱收取確認郵件以啟用您的帳戶!")
        
        user = authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError("帳號密碼錯誤!")

class AccountManagementBasicForm(forms.Form):
    first_name = forms.CharField(label='用戶名稱')
    username = forms.CharField(label='帳號')

class AccountManagementEmailForm(forms.Form):
    username = forms.CharField(widget=forms.HiddenInput(), label='帳號')
    email = forms.EmailField()

    def clean(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        email_count = User.objects.filter(email=email).count()
        if email_count > 0:
            raise forms.ValidationError("此信箱已經有人使用!")


class AccountManagementPasswordForm(forms.Form):
    username = forms.CharField(widget=forms.HiddenInput(), label='帳號')
    ori_password = forms.CharField(widget=forms.PasswordInput, label='舊密碼')
    new_password = forms.CharField(widget=forms.PasswordInput, label='新密碼')
    new_password_check = forms.CharField(widget=forms.PasswordInput, label='新密碼確認')

    def clean(self):
        username = self.cleaned_data.get('username')
        user = User.objects.filter(username=username)[0]
        ori_password = self.cleaned_data.get('ori_password')
        new_password = self.cleaned_data.get('new_password')
        new_password_check = self.cleaned_data.get('new_password_check')
        user = authenticate(username=username, password=ori_password)
        if user is None:
            raise forms.ValidationError("帳號密碼不正確!")
        if new_password != new_password_check:
            raise forms.ValidationError("新密碼確認不一致!")

        try:
            validate_password(new_password)
        except ValidationError as e:
            raise forms.ValidationError(e)


class ForgetPasswordForm(forms.Form):
    first_name = forms.CharField(label='用戶名稱', required=False)
    username = forms.CharField(label='帳號', required=False)
    email = forms.EmailField(required=False)

    def clean(self):
        first_name = self.cleaned_data.get('first_name')
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if first_name is None and username is None and email is None:
            raise forms.ValidationError("請至少輸入一個查詢欄位!")

        first_name = self.cleaned_data.get('first_name')
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        users = User.objects.filter(Q(first_name=first_name) | Q(username=username) | Q(email=email))
        if  users.count() == 0:
            raise forms.ValidationError("查無此使用者!")
            

class EmailResetPasswordForm(forms.Form):
    first_name = forms.CharField(label='用戶名稱', required=False)
    username = forms.CharField(label='帳號', required=False)
    email = forms.EmailField(required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, label='新密碼')
    new_password_check = forms.CharField(widget=forms.PasswordInput, label='新密碼確認')

    def clean(self):
        new_password = self.cleaned_data.get('new_password')
        new_password_check = self.cleaned_data.get('new_password_check')
        if new_password != new_password_check:
            raise forms.ValidationError("新密碼確認不一致")
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise forms.ValidationError(e)


class NoValidationEmailForm(forms.Form):
    username = forms.CharField(label='帳號')
    email = forms.EmailField()

    def clean(self):
        username = self.cleaned_data.get("username")
        users = User.objects.filter(username=username)
        if users.count() == 0:
            raise forms.ValidationError("查無此帳號")

        if users[0].is_active:
            raise forms.ValidationError("此帳號已經成功啟用，請直接登入系統。")
            
        



            