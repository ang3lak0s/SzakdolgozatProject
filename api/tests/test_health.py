from django.test import TestCase
from rest_framework import status


class ApiHealthCheckTests(TestCase):
    def test_api_root_endpoint(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'message': 'Hello World!'})

    def test_test_endpoint(self):
        response = self.client.get('/test/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'message': 'Hello World!'})
