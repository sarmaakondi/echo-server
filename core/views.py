import json

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
