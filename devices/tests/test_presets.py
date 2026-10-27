import os
import shutil
import tempfile
import json
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from devices.models import Preset

# Create an isolated temporary media root directory for testing uploads
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PresetApiTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Clean up temporary test media folder after tests finish
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Create User 1 and token
        self.user1 = User.objects.create_user(username='tester_one', password='password123')
        self.token1 = Token.objects.create(user=self.user1)

        # Create User 2 and token
        self.user2 = User.objects.create_user(username='tester_two', password='password123')
        self.token2 = Token.objects.create(user=self.user2)

        self.upload_url = reverse('upload_preset')
        self.presets_url = reverse('get_presets')

        # Sample Intel HEX test firmware content
        self.hex_content = (
            b":100000000C9434000C9451000C9451000C94510013\n"
            b":00000001FF\n"
        )

    def test_upload_preset_requires_authentication(self):
        response = self.client.post(self.upload_url, {'name': 'Test No Auth'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_presets_requires_authentication(self):
        response = self.client.get(self.presets_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_preset_success_with_json_config(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')

        firmware_file = SimpleUploadedFile(
            name='blink_atmega328p.hex',
            content=self.hex_content,
            content_type='text/plain'
        )
        config_data = {
            'baud': 115200,
            'pins': {'D13': 'OUTPUT', 'A0': 'INPUT'},
            'diag': {'check_ram': True, 'check_vcc': True}
        }

        payload = {
            'name': 'Blink Firmware V1',
            'description': 'Hardware blink firmware with pin config',
            'firmware_file': firmware_file,
            'config_json': json.dumps(config_data)
        }

        response = self.client.post(self.upload_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Blink Firmware V1')

        # Verify database record
        preset = Preset.objects.filter(name='Blink Firmware V1').first()
        self.assertIsNotNone(preset)
        self.assertEqual(preset.user, self.user1)
        self.assertEqual(preset.config_json, config_data)
        self.assertTrue(preset.firmware_file.name.startswith('firmwares/'))

    def test_upload_preset_corrupt_json_handled_gracefully(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')

        firmware_file = SimpleUploadedFile(
            name='test_corrupt.hex',
            content=self.hex_content,
            content_type='text/plain'
        )

        payload = {
            'name': 'Corrupt JSON Preset',
            'firmware_file': firmware_file,
            'config_json': '{invalid_json_string'
        }

        response = self.client.post(self.upload_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        preset = Preset.objects.filter(name='Corrupt JSON Preset').first()
        self.assertIsNotNone(preset)
        self.assertEqual(preset.config_json, {})

    def test_upload_preset_missing_file_fails(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        payload = {
            'name': 'Missing File Preset',
            'description': 'No firmware provided'
        }
        response = self.client.post(self.upload_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('firmware_file', response.data)

    def test_tenant_isolation_user_only_sees_own_presets(self):
        # Create presets for User 1
        file1 = SimpleUploadedFile('preset1.hex', self.hex_content)
        file2 = SimpleUploadedFile('preset2.hex', self.hex_content)
        Preset.objects.create(user=self.user1, name='User1 Preset Alpha', firmware_file=file1)
        Preset.objects.create(user=self.user1, name='User1 Preset Beta', firmware_file=file2)

        # Create preset for User 2
        file3 = SimpleUploadedFile('preset3.hex', self.hex_content)
        Preset.objects.create(user=self.user2, name='User2 Confidential Preset', firmware_file=file3)

        # Query as User 1
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.get(self.presets_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        names = [item['name'] for item in response.data]
        self.assertIn('User1 Preset Alpha', names)
        self.assertIn('User1 Preset Beta', names)
        self.assertNotIn('User2 Confidential Preset', names)

        # Query as User 2
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        response2 = self.client.get(self.presets_url)

        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.data), 1)
        self.assertEqual(response2.data[0]['name'], 'User2 Confidential Preset')
