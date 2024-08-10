from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, ProfileForm
from .models import Profile
from Dashboard.models import Auction,Category
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
import random
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
#from .models import Auction

# Create your views here.
def home(request):
    return render(request, "home.html", {
            "category":Category.objects.all()
        })

def aboutUs(request):
    return render(request,'aboutUs.html')  


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

@login_required
def profile_view(request):
    profile = request.user.profile
    won_auctions = Auction.objects.filter(winner=request.user)

    return render(request, 'profile_view.html', {
        'profile': profile,
        'won_auctions': won_auctions
    })

@login_required
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

@login_required
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

# written by sufi
#view for change password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

class ChangePasswordView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('User:user_login')
    template_name = 'change_password.html'


# view for reset password
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_message = ("We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder.")
    success_url = reverse_lazy('User:user_login')

def depo_otp_verification(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_in_session = request.session.get('otp')
        otp_expiry = datetime.strptime(request.session.get('otp_expiry'), '%Y-%m-%d %H:%M:%S')

        if datetime.now() > otp_expiry:
            messages.error(request, 'OTP has expired. Please request a new one.')
            return redirect('User:deposite')

        if entered_otp == otp_in_session:
            amount = request.session.get('amount')
            profile= Profile.objects.get(user=request.user)
            profile.amount+=int(amount)
            profile.save()

            del request.session['otp']
            del request.session['otp_expiry']
            del request.session['amount']
            return redirect('User:profile_view')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect("User:depo_verification")

    return render(request, 'otp_verification.html')

@login_required
def deposite(request):
    if request.method == 'POST':
        Amount = request.POST.get('Amount')
        print(Amount)
        if Amount:
            request.session['amount'] = Amount
            otp = ''.join(random.choices('0123456789', k=6))
            request.session['otp'] = otp
            request.session['otp_expiry'] = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
            
            send_mail(
                'OTP for Deposite Verification',
                f'Your OTP for verifing the Deposite is: {otp}',
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=False,
            )
            return redirect("User:depo_verification")
    return render(request,'deposite.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile
# from .forms import ProfilePicForm
from django.utils import timezone

@login_required
def upload_profile_pic(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = request.FILES.get('profile_picture')
        if form:
            profile = Profile.objects.get(user=request.user)
            profile.profile_picture = form
            profile.save()
            return redirect('User:profile_view')  
    return render(request, 'upload_profile.html', {'profile': profile})



@login_required
def confirm_membership(request):
    if request.method == 'POST':
        user_profile = Profile.objects.get(user=request.user)
        
        if user_profile.amount >= 10000:
            user_profile.amount -= 10000
            user_profile.activate_membership()
            user_profile.save()
            return redirect('User:profile_view') 
        else:
            return redirect('User:confirm_membership')
    
    return render(request, 'confirm_membership.html')

def membership(request):
    return render(request,"membership.html")

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Seller

@login_required
def confirm_seller_request(request):
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        
        # Check if the user is already a seller
        if not hasattr(profile, 'seller'):
            Seller.objects.create(profile=profile)
        
        profile.is_seller = True
        profile.save()
        return redirect('User:profile_view') 
    
    return render(request, 'confirm_seller.html')

def seller_profile_view(request,id):
    seller=Seller.objects.get(pk=id)
    print(seller)
    return render(request,'seller_profile.html',{'seller': seller})

