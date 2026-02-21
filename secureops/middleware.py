import time
from django.utils import timezone
from .models import LoginAttempt, BlockedIP
from django.http import HttpResponseForbidden

class BruteForceProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        
        # Check if IP is blocked
        blocked = BlockedIP.objects.filter(ip_address=ip).first()
        if blocked:
            if blocked.expires_at and blocked.expires_at < timezone.now():
                blocked.delete()
            else:
                return HttpResponseForbidden(f"Your IP {ip} is temporarily blocked due to suspicious activity. Reason: {blocked.reason}")

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
