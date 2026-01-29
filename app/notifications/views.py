from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponse

@login_required
def toggle_notification_channel(request):
    if not request.htmx or request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    channel = request.POST.get("channel")
    value = request.POST.get("value") == "true"

    if channel not in {"email", "web_push", "sms", "in_app", "whatsapp"}:
        return HttpResponseBadRequest("Invalid channel")

    prefs = request.user.notification_channels
    setattr(prefs, channel, value)
    prefs.save(update_fields=[channel])

    return HttpResponse(status=204)
