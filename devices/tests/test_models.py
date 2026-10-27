from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from devices.models import Preset


class PresetModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='embedded_dev',
            password='password123',
            email='dev@example.com'
        )
        self.dummy_file = SimpleUploadedFile(
            name='test_firmware.hex',
            content=b':00000001FF\n',
            content_type='text/plain'
        )

    def test_preset_creation_and_str(self):
        preset = Preset.objects.create(
            user=self.user,
            name='Blink LED Preset',
            description='Test LED blink firmware for ATmega328P',
            firmware_file=self.dummy_file,
            config_json={'baud': 115200, 'pin': 13}
        )

        self.assertEqual(str(preset), 'embedded_dev - Blink LED Preset')
        self.assertEqual(preset.user, self.user)
        self.assertEqual(preset.name, 'Blink LED Preset')
        self.assertEqual(preset.config_json['baud'], 115200)
        self.assertIsNotNone(preset.created_at)
        self.assertIsNotNone(preset.last_updated_at)

    def test_preset_default_config_json(self):
        preset = Preset.objects.create(
            user=self.user,
            name='Default Config Preset',
            firmware_file=self.dummy_file
        )
        self.assertIsInstance(preset.config_json, dict)
        self.assertEqual(preset.config_json, {})

    def test_user_cascade_deletion(self):
        Preset.objects.create(
            user=self.user,
            name='Preset To Cascade',
            firmware_file=self.dummy_file
        )
        self.assertEqual(Preset.objects.count(), 1)
        
        # Deleting the user must cascade delete the preset
        self.user.delete()
        self.assertEqual(Preset.objects.count(), 0)
