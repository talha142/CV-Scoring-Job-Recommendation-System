from django.contrib import admin

# Register your models here.
# core/admin.py
from django.contrib import admin
from .models import Profile, UploadedCV

admin.site.register(Profile)
admin.site.register(UploadedCV)
