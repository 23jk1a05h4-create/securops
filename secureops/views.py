from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import LoginAttempt, CustomUser, BlockedIP
from django.utils import timezone
import pyotp
from datetime import timedelta

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        ip = get_client_ip(request)
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Check if 2FA is needed
            if user.is_2fa_enabled:
                request.session['pre_otp_user_id'] = user.id
                return redirect('otp_verify')
            
            login(request, user)
            LoginAttempt.objects.create(username=username, ip_address=ip, success=True, password_attempted=password)
            return redirect('dashboard')
        else:
            LoginAttempt.objects.create(username=username, ip_address=ip, success=False, password_attempted=password)
            # Brute force logic
            recent_fails = LoginAttempt.objects.filter(
                ip_address=ip, 
                success=False, 
                timestamp__gte=timezone.now() - timedelta(minutes=5)
            ).count()
            
            if recent_fails >= 3:
                BlockedIP.objects.get_or_create(
                    ip_address=ip,
                    defaults={'reason': 'Too many failed login attempts', 'expires_at': timezone.now() + timedelta(minutes=15)}
                )
            
            return render(request, 'login.html', {'error': 'Invalid credentials'})
            
    return render(request, 'login.html')

def otp_verify(request):
    user_id = request.session.get('pre_otp_user_id')
    if not user_id:
        return redirect('login')
    
    user = CustomUser.objects.get(id=user_id)
    if request.method == 'POST':
        otp = request.POST.get('otp')
        totp = pyotp.TOTP(user.otp_secret)
        if totp.verify(otp):
            login(request, user)
            del request.session['pre_otp_user_id']
            return redirect('dashboard')
        else:
            return render(request, 'otp_verify.html', {'error': 'Invalid OTP'})
            
    return render(request, 'otp_verify.html')

@login_required
def dashboard(request):
    recent_attempts = LoginAttempt.objects.filter(username=request.user.username).order_by('-timestamp')[:10]
    all_logs = LoginAttempt.objects.all().order_by('-timestamp')[:50]
    return render(request, 'dashboard.html', {
        'recent_attempts': recent_attempts,
        'all_logs': all_logs
    })

def logout_view(request):
    logout(request)
    return redirect('home')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
