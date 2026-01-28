from django.shortcuts import render
from template_map.errors import Errors


def custom_404(request, exception):
    return render(request, Errors.ERROR_404, status=404)


def custom_500(request):
    return render(request, Errors.ERROR_500, status=500)
