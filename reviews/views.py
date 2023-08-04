from django.shortcuts import render
from django.shortcuts import get_object_or_404

# models
from .models import Review

# serializer
from .serializers import ReviewSerializer

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404