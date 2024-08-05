import json

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def register_user(request):
    data = json.loads(request.body)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.objects.filter(username=username).exists():
        return JsonResponse({"errors": "Username already exists"}, status=400)

    user = User.objects.create(
        username=username, email=email, password=make_password(password)
    )

    return JsonResponse({"username": user.username})


@csrf_exempt
@require_POST
def login_user(request):
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")
    user = authenticate(username=username, password=password)

    if user is not None:
        auth_login(request, user)
        return JsonResponse({"username": user.username})

    return JsonResponse({"errors": "Invalid credentials"}, status=400)


@csrf_exempt
@require_POST
def logout_user(request):
    auth_logout(request)
    return JsonResponse({"message": "Logged out"})
