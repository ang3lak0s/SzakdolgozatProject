from rest_framework import serializers
from .models import Preset

class PresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preset
        fields = ['id', 'name', 'description', 'firmware_file', 'config_json', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'config_json': {'required': False},
            'description': {'required': False}
        }