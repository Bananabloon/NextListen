from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Genre, Media, PreferenceVector, UserFeedback

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('spotifyUserId', 'displayName', 'is_staff', 'is_superuser')
    search_fields = ('spotifyUserId', 'displayName')
    ordering = ('spotifyUserId',)
    fieldsets = (
        (None, {'fields': ('spotifyUserId', 'displayName', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('spotifyUserId', 'displayName', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(User, UserAdmin)
admin.site.register(Genre)
admin.site.register(Media)
admin.site.register(PreferenceVector)
admin.site.register(UserFeedback)