from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Media, UserFeedback


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("spotify_user_id", "display_name", "is_staff", "is_superuser")
    search_fields = ("spotify_user_id", "display_name")
    ordering = ("spotify_user_id",)
    fieldsets = (
        (None, {"fields": ("spotify_user_id", "display_name", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "spotify_user_id",
                    "display_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Media)
admin.site.register(UserFeedback)
