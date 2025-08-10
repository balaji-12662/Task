from functools import wraps
from django.http import JsonResponse
from .models import SessionToken

def token_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Token "):
            return JsonResponse({"error": "Authorization header required (Token <token>)"}, status=401)
        token = auth.split(" ", 1)[1].strip()
        if not token:
            return JsonResponse({"error": "token missing"}, status=401)
        try:
            sess = SessionToken.objects.get(token=token)
        except SessionToken.DoesNotExist:
            return JsonResponse({"error": "invalid token"}, status=401)
        if sess.is_expired():
            sess.delete()
            return JsonResponse({"error": "token expired"}, status=401)
        request.teacher = sess.teacher
        request.session_token = sess
        return view(request, *args, **kwargs)
    return wrapped
