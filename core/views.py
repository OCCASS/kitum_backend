from django.http import JsonResponse


def handler404(request, *args, **kwargs):
    return JsonResponse({"detail": "Not found."})


def handler500(request, *args, **kwargs):
    return JsonResponse({"detail": "Server error occurred."})
