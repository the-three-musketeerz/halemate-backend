from django.contrib import admin

from halemate_auth.models import User, PasswordReset

admin.site.register(User)
admin.site.register(PasswordReset)
