from django.http import JsonResponse


def home(request):
    data = {"message": "welcome to Django!"}
    return JsonResponse(data, safe=False)
