from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

