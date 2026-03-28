from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from registry_utils import get_registered_model


@login_required
def toggle_notification_channel(request):
    if not request.htmx or request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    channel = request.POST.get("channel")
    value = request.POST.get("value") == "true"
    token = request.POST.get("token", None)
    print(f"Received toggle for channel: {channel}, value: {value}, token: {token}")

    if channel not in {"email", "web_push", "sms", "in_app", "whatsapp"}:
        return HttpResponseBadRequest("Invalid channel")

    prefs = request.user.notification_channels
    setattr(prefs, channel, value)
    prefs.save(update_fields=[channel])
    
    WebPushDeviceToken = get_registered_model("notifications", "WebPushDeviceToken")
    
    WebPushDeviceToken.objects.update_or_create(
        token=token,
        defaults={
            "user": request.user,
            "is_active": True
        }
    )

    return HttpResponse(status=204)

@csrf_exempt
def service_worker(request):
    from django.conf import settings
    
    content = render_to_string(
        "notifications/firebase-messaging-sw.js",
        {
            "FIREBASE_API_KEY": settings.FIREBASE_API_KEY,
            "FIREBASE_AUTH_DOMAIN": settings.FIREBASE_AUTH_DOMAIN,
            "FIREBASE_PROJECT_ID": settings.FIREBASE_PROJECT_ID,
            "FIREBASE_STORAGE_BUCKET": settings.FIREBASE_STORAGE_BUCKET,
            "FIREBASE_MESSAGING_SENDER_ID": settings.FIREBASE_MESSAGING_SENDER_ID,
            "FIREBASE_APP_ID": settings.FIREBASE_APP_ID,
            "FIREBASE_MEASUREMENT_ID": settings.FIREBASE_MEASUREMENT_ID,
        },
        request=request
    )

    return HttpResponse(content, content_type="application/javascript")