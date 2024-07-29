# admin.py
from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address', 'is_premium', 'membership_start_date', 'membership_end_date')
    search_fields = ('user__username', 'phone', 'address')
    list_filter = ('is_premium', 'membership_start_date', 'membership_end_date')
    readonly_fields = ('membership_start_date', 'membership_end_date')
    fieldsets = (
        (None, {
            'fields': ('user', 'phone', 'address')
        }),
        ('Membership Info', {
            'fields': ('is_premium', 'membership_start_date', 'membership_end_date'),
            'classes': ('collapse',),
        }),
        ('Profile Details', {
            'fields': ('ratings_sum', 'ratings_count', 'birth_date', 'amount', 'profile_picture'),
        }),
    )

admin.site.register(Profile, ProfileAdmin)
