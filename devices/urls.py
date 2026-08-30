from django.urls import path
from .views import register_user, login_user, upload_preset, get_presets

urlpatterns = [
    path('api/register/', register_user, name='register'),
    path('api/login/', login_user, name='login'),
    path('api/upload/', upload_preset, name='upload_preset'),
    path('api/presets/', get_presets, name='get_presets')
]