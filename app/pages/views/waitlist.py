from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from datetime import datetime
import json, os


class WaitingListView(View):
    template_name = "waiting-list.html"

    def get(self, request: HttpRequest):
        launch_date = datetime(2026, 7, 15, 11, 50, 59)
        return render(request, self.template_name, {"launch_date": launch_date})

    def post(self, request: HttpRequest):
        if not request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "message": "Bad request."}, status=400)

        email = request.POST.get('email', '').strip().lower()
        role = request.POST.get('role', '').strip().lower()
        valid_roles = ['client', 'provider', 'both']

        if not email or role not in valid_roles:
            return JsonResponse({
                "status": "error", 
                "message": "Please provide a valid business email and select your role."
            }, status=400)
            
        if "@" not in email:
            return JsonResponse({"status": "error", "message": "A valid email is required."}, status=400)

        storage = WaitlistStorage()
        success, reason = storage.add_entry(email, role)
        
        if reason == "already_exists":
            return JsonResponse({
                "status": "success", 
                "message": "Access reserved! We'll be in touch."
            })

        if success:
            return JsonResponse({
                "status": "success", 
                "message": "Access Secured. Welcome to Servio."
            })
        
        return JsonResponse({"status": "error", "message": "Our engine hit a snag. Please try again later."}, status=500)

    
class WaitlistStorage:
    """Handles persistent storage for the waitlist using a JSON file."""
    
    def __init__(self):
        self.file_path = os.path.join(settings.BASE_DIR, 'private_data', 'waitlist.json')
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)

    def get_all(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def add_entry(self, email, role):
        data = self.get_all()
        if any(entry['email'] == email for entry in data):
            return False, "already_exists"

        data.append({
            "email": email,
            "role": role,
            "timestamp": datetime.now().isoformat()
        })

        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        return True, "added"