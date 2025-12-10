# app/payouts/tests.py
from decimal import Decimal
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from .models import Payout


class PayoutAPITestCase(APITestCase):

    def setUp(self):
        self.url = reverse('payouts-list')

    def test_create_payout_success(self):
        """Успешное создание заявки"""
        payload = {
            "amount": "499.99",
            "currency": "USD",
            "recipient": "J D, IBAN: DE89370400440532013000",
            "description": "Тестовая выплата"
        }

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payout.objects.count(), 1)

        payout = Payout.objects.first()
        self.assertEqual(payout.amount, Decimal("499.99"))
        self.assertEqual(payout.currency, "USD")
        self.assertEqual(payout.status, Payout.Status.PENDING)
        self.assertIn("id", response.data)

    @patch('payouts.views.process_payout.delay')
    def test_celery_task_called_on_create(self, mock_delay):
        """При создании заявки вызывается Celery-задача"""
        payload = {
            "amount": "777.00",
            "currency": "EUR",
            "recipient": "Alice"
        }

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payout = Payout.objects.first()

        # Проверка delay() был вызван с правильным id
        mock_delay.assert_called_once_with(payout.id)
