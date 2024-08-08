from django.contrib.auth.models import User
from django.db import models


class Echo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="echoes")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_echoes", blank=True)

    def __str__(self):
        return f"Echo by {self.user.username}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    echo = models.ForeignKey(Echo, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Echo {self.echo.id}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"
