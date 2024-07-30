# admin.py
from django.contrib import admin
from .models import Profile,Seller

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address','is_seller', 'is_premium', 'membership_start_date', 'membership_end_date')
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
            'fields': ( 'birth_date', 'amount', 'profile_picture'),
        }),
    )


class SellerAdmin(admin.ModelAdmin):
    list_display = ('profile','total_properties','total_ratings','average_rating')
    list_filter = ('average_rating','total_ratings','total_properties')

    search_fields = ('profile__user__username',)  # Allows searching by username

    fieldsets = (
        (None, {
            'fields': ('profile',)
        }),
        ('Statistics', {
            'fields': ('total_properties', 'total_ratings', 'average_rating'),
            'classes': ('collapse',),
        }),
        ('Rating Details', {
            'fields': ('rating_sum',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('rating_sum', 'total_ratings', 'average_rating')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Seller,SellerAdmin)
