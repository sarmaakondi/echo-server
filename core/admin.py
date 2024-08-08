from django.contrib import admin

from .models import Comment, Echo, Profile

admin.site.register([Comment, Echo, Profile])
