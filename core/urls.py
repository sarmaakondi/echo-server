from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register_user, name="register_user"),
    path("login/", views.CustomTokenObtainPairSerializer.as_view(), name="login_user"),
    path("refresh/", views.refresh_token),
    path("create-echo/", views.create_echo, name="create_echo"),
    path("create-comment/", views.create_comment, name="create_comment"),
    path("like-echo/<int:echo_id>/", views.like_echo, name="like_echo"),
    path("list-echoes/", views.list_echoes, name="list_echoes"),
    path("list-liked-echoes/", views.list_liked_echoes, name="list_liked_echoes"),
    path("list-echoes-no-auth/", views.list_echoes_no_auth, name="list_echoes_no_auth"),
    path("upload-profile-pic/", views.upload_profile_pic, name="upload_profile_pic"),
]
