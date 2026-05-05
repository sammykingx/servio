from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

import json

class WaitingListView(View):
    template_name = "waiting-list.html"

    def get(self, request):
        launch_date = datetime(2026, 7, 6)
        return render(request, self.template_name, {"launch_date": launch_date})

    def post(self, request):
        if not request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"message": "Bad request."}, status=400)

        
        body = json.loads(request.body)
        email = body.get("email", "").strip()
        role  = body.get("role", "").strip()

        if not email:
            return JsonResponse({"message": "Email is required."}, status=400)

        # TODO: save to your model here
        # WaitlistEntry.objects.create(email=email, role=role)

        return JsonResponse({"message": "You're on the list! We'll be in touch."})
