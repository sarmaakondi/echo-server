from django.contrib import admin

from .models import Comment, Echo

admin.site.register([Comment, Echo])
