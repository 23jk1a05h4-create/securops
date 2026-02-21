from django.contrib import admin
from .models import CustomUser, LoginAttempt, BlockedIP

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_2fa_enabled', 'is_staff')
    list_filter = ('is_2fa_enabled', 'is_staff', 'is_superuser')

@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('username', 'password_attempted', 'ip_address', 'timestamp', 'success')
    list_filter = ('success', 'timestamp')
    search_fields = ('username', 'ip_address')
    readonly_fields = ('timestamp',)

@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'reason', 'blocked_at', 'expires_at')
    search_fields = ('ip_address',)
