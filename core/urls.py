from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register_user, name="register_user"),
    path("login/", views.CustomTokenObtainPairSerializer.as_view(), name="login_user"),
    path("refresh/", views.refresh_token),
]
