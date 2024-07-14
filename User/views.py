from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, ProfileForm
from .models import Profile
from Dashboard.models import Auction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
import random
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from datetime import datetime, timedelta

# Create your views here.
def home(request):
    return render(request, "home.html", {
            "auctions": Auction.objects.filter(approval_status='pending').order_by('-creation_date')
        })

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            request.session['user_form_data'] = user_form.cleaned_data
            request.session['profile_form_data'] = {
                'phone': profile_form.cleaned_data['phone'],
                'address': profile_form.cleaned_data['address'],
                'birth_date': profile_form.cleaned_data['birth_date'].strftime('%Y-%m-%d') if profile_form.cleaned_data['birth_date'] else None,
            }
            
            otp = ''.join(random.choices('0123456789', k=6))
            request.session['otp'] = otp
            request.session['otp_expiry'] = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
            
            send_mail(
                'OTP for Profile Verification',
                f'Your OTP for profile verification is: {otp}',
                settings.EMAIL_HOST_USER,
                [user_form.cleaned_data['email']],
                fail_silently=False,
            )

            return redirect("User:mail_verification")
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileForm()

    return render(request, 'register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def mail_verification(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_in_session = request.session.get('otp')
        otp_expiry = datetime.strptime(request.session.get('otp_expiry'), '%Y-%m-%d %H:%M:%S')

        if datetime.now() > otp_expiry:
            messages.error(request, 'OTP has expired. Please register again.')
            return redirect('User:register')

        if entered_otp == otp_in_session:
            del request.session['otp']
            del request.session['otp_expiry']

            user_form_data = request.session.get('user_form_data')
            profile_form_data = request.session.get('profile_form_data')

            birth_date_str = profile_form_data.get('birth_date')
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None

            user = UserRegistrationForm(user_form_data).save()
            profile_data = {
                'phone': profile_form_data['phone'],
                'address': profile_form_data['address'],
                'birth_date': birth_date,
            }
            Profile.objects.create(user=user, **profile_data)

            del request.session['user_form_data']
            del request.session['profile_form_data']
            return redirect('User:user_login')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect("User:mail_verification")

    return render(request, 'otp_verification.html')

def user_login(request):
    if request.method == 'POST':
        loginform = AuthenticationForm(request, request.POST)
        if loginform.is_valid():
            user_name = loginform.cleaned_data['username']
            user_pass = loginform.cleaned_data['password']
            user = authenticate(request, username=user_name, password=user_pass)
            if user is not None:
                login(request, user)
                return redirect('User:profile_view')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
                return redirect('User:user_login')
    else:
        loginform = AuthenticationForm()
    return render(request, 'login.html', {'form': loginform, 'type': 'Login'})

def user_logout(request):
    logout(request)
    return redirect('User:home')

def profile_view(request):
    profile = request.user.profile
    return render(request, 'profile_view.html', {'profile': profile})

def profile_update(request):
    if request.user.is_authenticated:
        otp = ''.join(random.choices('0123456789', k=6))
        request.session['otp'] = otp
        request.session['otp_expiry'] = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
        
        send_mail(
            'OTP for Profile Update',
            f'Your OTP for profile update is: {otp}',
            settings.EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=False,
        )
        return redirect("User:otp_verification")
    else:
        return redirect("User:home")

def otp_verification(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_in_session = request.session.get('otp')
        otp_expiry = datetime.strptime(request.session.get('otp_expiry'), '%Y-%m-%d %H:%M:%S')

        if datetime.now() > otp_expiry:
            messages.error(request, 'OTP has expired. Please request a new one.')
            return redirect('User:profile_update')

        if entered_otp == otp_in_session:
            del request.session['otp']
            del request.session['otp_expiry']
            return redirect('User:profile_update_page')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect("User:otp_verification")

    return render(request, 'otp_verification.html')

def profile_update_page(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect("User:profile_view")
    else:
        profile_form = ProfileForm(instance=profile)

    return render(request, 'profile_update.html', {
        'profile_form': profile_form
    })

