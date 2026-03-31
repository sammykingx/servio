from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.views.generic import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from .channels.push.push_manager import PushManager
from .domain.exceptions import NotificationChannelError
from .domain.schemas import NotificationChannels, NotificationPayload
from pydantic import ValidationError
import json


class ToggleNotifications(LoginRequiredMixin, View):
    """
    An endpoint to enable or disable notification delivery channels for a user.

    This view handles the logic for updating a user's notification preferences 
    (e.g., Email, SMS, Web Push) and manages external tokens for push services 
    within a transaction-safe environment.
    """
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to update notification channel states.

        The request body must be a JSON payload containing the channel type, 
        the desired state (boolean), and an optional device token.

        Returns:
            HttpResponse: 
                - 204: Successfully updated.
                - 400: Invalid JSON or failed Pydantic validation.
                - 422: Logical error during the toggle process.
                - 500: Unexpected server error.
        """
        try:
            data = NotificationPayload(**json.loads(request.body))
            self.toggle_notification_channels(data)
            
        except json.JSONDecodeError:
            return HttpResponse(status=400, content="Invalid JSON payload")
            
        except ValidationError as e:
            from formatters.pydantic_formatter import format_pydantic_errors
            formatted_errors = format_pydantic_errors(e)
            
            return HttpResponse(status=400, content=str(e))
        
        except NotificationChannelError as e:
            print(f"NotificationChannelError: {str(e)}")
            return HttpResponse(status=422, content=str(e))
        
        except Exception:
            return HttpResponse(status=500, content="An unexpected error occurred")
            
        return HttpResponse(status=204)
    
    @transaction.atomic
    def toggle_notification_channels(self, payload: NotificationPayload):
        """
        Updates the user's notification preferences in the database.

        If the channel being updated is 'WEB_PUSH' and a token is provided, 
        this method also invokes the PushManager to register or update the 
        device subscription.

        Args:
            payload (NotificationPayload): A validated data object containing:
                - channel: The attribute name on the preference model.
                - state: Boolean value for the new status.
                - token: Optional device token for push services.

        Raises:
            NotificationChannelError: If the database update or push registration fails.
        """
        try:
            prefs = self.request.user.notification_channels
            setattr(prefs, payload.channel, payload.state)
            prefs.save(update_fields=[payload.channel])
            
            if payload.channel == NotificationChannels.WEB_PUSH and payload.token:
                push_manager = PushManager(user=self.request.user)
                push_manager.handle_token_state(payload)
                
        except Exception as e:
            raise NotificationChannelError(str(e))

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

    