import json
import re

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Comment, Echo
from .serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


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


@method_decorator(csrf_exempt, name="dispatch")
class LoginUser(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        # Read username and password from request body
        username = data.get("username")
        password = data.get("password")

        # Check for empty fields
        if not username or not password:
            return JsonResponse(
                {"errors": "username and password are required"}, status=400
            )

        # Authenticate user
        user = authenticate(username=username, password=password)

        # Generate and send the access token
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            access_token["username"] = user.username

            return JsonResponse(
                {
                    "refresh": str(refresh),
                    "access": str(access_token),
                }
            )

        return JsonResponse({"errors": "Invalid credentials"}, status=400)


def refresh_token(request):
    # Ensure to receive valid JSON data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"errors": "Invalid JSON data"}, status=400)

    # Check for refresh token
    refresh_token = data.get("refresh")
    if not refresh_token:
        return JsonResponse({"errors": "Refresh token is required"}, status=400)

    try:
        refresh = RefreshToken(refresh_token)
        new_access_token = refresh.access_token
        return JsonResponse({"access": str(new_access_token)})
    except Exception as e:
        return JsonResponse({"errors": str(e)}, status=400)


@csrf_exempt
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_echo(request):
    # Ensure to receive valid JSON data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"errors": "Invalid JSON data"}, status=400)

    # Read the content from the request body
    content = data.get("content")

    # Check content
    if not content:
        return JsonResponse({"errors": "Content cannot be empty"}, status=400)

    # Create Echo
    echo = Echo.objects.create(
        user=request.user,
        content=content,
    )

    return JsonResponse(
        {
            "id": echo.id,
            "user": echo.user.username,
            "content": echo.content,
            "created_at": echo.created_at,
            "likes": 0,
            "comments": [],
        },
        status=201,
    )


@csrf_exempt
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_comment(request):
    # Ensure to receive valid JSON data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"errors": "Invalid JSON data"}, status=400)

    # Read the content from the request body
    echo_id = data.get("echo_id")
    content = data.get("content")

    # Check for empty fields
    if not echo_id or not content:
        return JsonResponse({"errors": "Echo ID and content are required"}, status=400)

    # Create Comment
    echo = get_object_or_404(Echo, id=echo_id)
    Comment.objects.create(
        user=request.user,
        echo=echo,
        content=content,
    )

    response_data = {
        "id": echo.id,
        "user": echo.user.username,
        "content": echo.content,
        "created_at": echo.created_at,
        "likes": echo.likes.count(),
        "is_liked": request.user in echo.likes.all(),
        "comments": [
            {
                "id": comment.id,
                "user": comment.user.username,
                "content": comment.content,
                "created_at": comment.created_at,
            }
            for comment in echo.comments.all().order_by("-created_at")
        ],
    }

    return JsonResponse(response_data, status=201)


@csrf_exempt
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def like_echo(request, echo_id):
    # Get echo and user details
    echo = get_object_or_404(Echo, id=echo_id)
    user = request.user

    # Like/UnLike the echo
    is_liked = user in echo.likes.all()
    if is_liked:
        echo.likes.remove(user)
    else:
        echo.likes.add(user)

    response_data = {
        "id": echo.id,
        "user": echo.user.username,
        "content": echo.content,
        "created_at": echo.created_at,
        "likes": echo.likes.count(),
        "is_liked": not is_liked,
        "comments": [
            {
                "id": comment.id,
                "user": comment.user.username,
                "content": comment.content,
                "created_at": comment.created_at,
            }
            for comment in echo.comments.all().order_by("-created_at")
        ],
    }

    return JsonResponse(response_data, status=200)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_echoes(request):
    # Get all the latest echoes
    echoes = Echo.objects.all().order_by("-created_at")[:20]

    # Append required details into a list and return
    user = request.user
    echo_list = []
    for echo in echoes:
        is_liked = user in echo.likes.all()
        echo_list.append(
            {
                # "user_1": request.user,
                "id": echo.id,
                "user": echo.user.username,
                "content": echo.content,
                "created_at": echo.created_at,
                "likes": echo.likes.count(),
                "is_liked": is_liked,
                "comments": [
                    {
                        "id": comment.id,
                        "user": comment.user.username,
                        "content": comment.content,
                        "created_at": comment.created_at,
                    }
                    for comment in echo.comments.all().order_by("-created_at")
                ],
            }
        )

    return JsonResponse(echo_list, safe=False)


def list_echoes_no_auth(request):
    # Get all the latest echoes
    echoes = Echo.objects.all().order_by("-created_at")[:20]

    # Append required details into a list and return
    echo_list = []
    for echo in echoes:
        echo_list.append(
            {
                # "user_1": request.user,
                "id": echo.id,
                "user": echo.user.username,
                "content": echo.content,
                "created_at": echo.created_at,
                "likes": echo.likes.count(),
                "comments": [
                    {
                        "id": comment.id,
                        "user": comment.user.username,
                        "content": comment.content,
                        "created_at": comment.created_at,
                    }
                    for comment in echo.comments.all().order_by("-created_at")
                ],
            }
        )

    return JsonResponse(echo_list, safe=False)
