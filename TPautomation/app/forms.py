from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class SignUpForm(forms.Form):
    first_name = forms.CharField(label='公司名稱')
    username = forms.CharField(label='帳號')
    password = forms.CharField(widget=forms.PasswordInput, label='密碼')
    password_check = forms.CharField(widget=forms.PasswordInput, label='密碼確認')
    email = forms.EmailField()

    def clean(self):
        super().clean()
        username_count = User.objects.filter(username=self.cleaned_data['username']).count()
        if username_count>0:
            raise forms.ValidationError("此帳號已經有人使用!")
        email_count = User.objects.filter(email=self.cleaned_data['email']).count()
        if email_count>0:
            raise forms.ValidationError("此信箱已經註冊!")
        first_name_count = User.objects.filter(first_name=self.cleaned_data['first_name']).count()
        if first_name_count>0:
            raise forms.ValidationError("此公司名稱已經註冊!")
        if self.cleaned_data['password'] != self.cleaned_data['password_check']:
            raise forms.ValidationError("輸入帳號與確認帳號不一致!")

class LogInForm(forms.Form):
    username = forms.CharField(label='帳號')
    password = forms.CharField(widget=forms.PasswordInput, label='密碼')
    
    def clean(self):
        super().clean()
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is None:
            if User.objects.filter(username=username).count() > 0: 
                raise forms.ValidationError("請至信箱收取確認郵件以啟用您的帳戶!")
            else:
                raise forms.ValidationError("帳號密碼錯誤!")