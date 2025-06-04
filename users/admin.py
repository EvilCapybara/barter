from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User
# from ads.models import Ad

# Register your models here.

admin.site.register(User, UserAdmin)
