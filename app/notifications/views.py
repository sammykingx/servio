from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from .channels.push.push_manager import PushManager
from .domain.schemas import NotificationChannels, NotificationPayload
from pydantic import ValidationError
import json


@login_required
def toggle_notification_channel(request):
    try:
        data = NotificationPayload(**json.loads(request.body))
        toggle_notification_channels(data, request.user)
        
    except json.JSONDecodeError:
        return HttpResponse(status=400, content="Invalid JSON payload")
        
    except ValidationError as e:
        from formatters.pydantic_formatter import format_pydantic_errors
        formatted_errors = format_pydantic_errors(e.errors())
        return HttpResponse(status=400, content=str(e))
    
    except Exception:
        return HttpResponse(status=500, content="An unexpected error occurred")
        
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


def toggle_notification_channels(payload: NotificationPayload, user):
    with transaction.atomic():
        prefs = user.notification_channels
        setattr(prefs, payload.channel, payload.state)
        prefs.save(update_fields=[payload.channel])
        
        if payload.channel == NotificationChannels.WEB_PUSH and payload.token:
            push_manager = PushManager(user)
            push_manager.create_object(payload.channel, payload.token, payload.state)
            
    