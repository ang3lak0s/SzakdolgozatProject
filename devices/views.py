from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Preset
from .serializers import PresetSerializer

import json

@api_view(['POST'])
@permission_classes([IsAuthenticated]) # Only logged-in users can upload
def upload_preset(request):
    data = request.data.copy()
    if 'config_json' in data:
        if isinstance(data['config_json'], str):
            try:
                data['config_json'] = json.loads(data['config_json']) if data['config_json'].strip() else {}
            except Exception:
                data['config_json'] = {}
    else:
        data['config_json'] = {}

    serializer = PresetSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_presets(request):
    # Fetch presets belonging ONLY to the logged-in user, newest first
    presets = Preset.objects.filter(user=request.user).order_by('-created_at')
    serializer = PresetSerializer(presets, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def register_user(request):
    data = request.data
    try:
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            email=data.get('email', '')
        )
        return Response({"message": "Sikeres regisztráció!"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "message": "Sikeres belépés!"})
    else:
        return Response({"error": "Hibás adatok!"}, status=status.HTTP_401_UNAUTHORIZED)

