from django.shortcuts import render

# Create your views here.
# /url/views.py
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from .models import URL
from rest_framework.decorators import api_view
from django.http import JsonResponse
import hashlib
from .serializers import URLSerializer
from rest_framework.response import Response
import json


# (... previous function code ...)
@api_view(["POST"])
def create_short_url(request):
    original_url = request.data["url"]

    if "url" in request.data:
        urlRecord = URL.objects.get(url=original_url)
        if bool(urlRecord):
            serializer = URLSerializer(urlRecord)
            return JsonResponse(
                {"duplicate url, short_url": f"/url/{serializer.data['hash']}/"},
                status=204,
            )
        else:
            # Generate a unique hash for the URL
            hash_value = hashlib.md5(original_url.encode()).hexdigest()[:10]
            # Create a new URL object in the database
            URL.objects.create(hash=hash_value, url=original_url)
            # Return the shortened URL in the response
            return JsonResponse({"short_url": f"/url/{hash_value}/"}, status=201)
    return JsonResponse({"error": "Invalid request data"}, status=400)


@api_view(["GET"])
def get_url_stats(request, hash):
    try:
        url = URL.objects.get(hash=hash)
        serializer = URLSerializer(url)
        return Response(serializer.data)
    except URL.DoesNotExist:
        return Response({"error": "Short URL not found"}, status=404)


def redirect_original_url(request, hash):
    try:
        url = URL.objects.get(hash=hash)
        url.visits += 1  # Increment visits count
        url.save()
        return redirect(url.url)
    except URL.DoesNotExist:
        return HttpResponseNotFound("Short URL not found")


def simple_ui(request):
    ## Get all urls
    urls = URL.objects.all()
    ## Render template
    return render(request, "index.html", {"urls": urls})
