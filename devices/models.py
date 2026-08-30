from django.db import models
from django.contrib.auth.models import User

class Preset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='presets')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    firmware_file = models.FileField(upload_to='firmwares/')

    config_json = models.JSONField(help_text='I/O pinek és opcionális diagnosztikai paraméterek', default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

