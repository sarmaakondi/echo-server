import json
import re

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
    # Ensure to receive valid JSON data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"errors": "Invalid JSON data"}, status=400)

    # Read username, email and password from request body
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Check for required fields
    if not username or not email or not password:
        return JsonResponse(
            {"errors": "username, email and password are required"}, status=400
        )

    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return JsonResponse({"errors": "Invalid email format"}, status=400)

    # Check password strength
    if len(password) < 6:
        return JsonResponse({"errors": "Password must be at least 6 characters long"})

    # Check for duplicate username or email
    if User.objects.filter(username=username).exists():
        return JsonResponse({"errors": "Username already exists"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"errors": "Email already registered"}, status=400)

    # Create the user
    user = User.objects.create(
        username=username, email=email, password=make_password(password)
    )

    return JsonResponse({"username": user.username})


@csrf_exempt
@require_POST
def login_user(request):
    # Ensure to receive valid JSON data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"errors": "Invalid JSON data"}, status=400)

    # Read username and password from request body
    username = data.get("username")
    password = data.get("password")

    # Check for empty fields
    if not username or not password:
        return JsonResponse(
            {"errors": "username and password are required"}, status=400
        )

    # Check if the user is already logged in
    if request.user.is_authenticated:
        return JsonResponse({"errors": "User is already logged in"}, status=400)

    # Authenticate user
    user = authenticate(username=username, password=password)

    # Login user
    if user is not None:
        auth_login(request, user)
        return JsonResponse({"username": user.username})

    return JsonResponse({"errors": "Invalid credentials"}, status=400)


@csrf_exempt
@require_POST
def logout_user(request):
    # Check for logged in user
    if not request.user.is_authenticated:
        return JsonResponse({"errors": "No user is currently logged in"}, status=400)

    # Logout the current user and send response
    auth_logout(request)
    return JsonResponse({"message": "Logged out"})
