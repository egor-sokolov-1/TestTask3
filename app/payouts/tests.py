# app/payouts/tests.py
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

from .models import Payout


class PayoutCreationTest(APITestCase):
    """Тесты создания выплаты"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("payouts-list")
        self.valid_payload = {
            "amount": "499.99",
            "currency": "USD",
            "recipient": "John Doe, IBAN: DE89370400440532013000",
            "description": "Тестовая выплата",
        }

    def test_create_payout_success(self):
        """ТЕСТ 1: Успешное создание заявки"""
        # проверяем реальное создание
        response = self.client.post(self.url, self.valid_payload, format="json")

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # объект создан в базе
        self.assertEqual(Payout.objects.count(), 1)

        # поля созданного объекта
        payout = Payout.objects.first()
        self.assertEqual(payout.amount, Decimal("499.99"))
        self.assertEqual(payout.currency, "USD")
        self.assertEqual(payout.recipient, "John Doe, IBAN: DE89370400440532013000")
        self.assertEqual(payout.description, "Тестовая выплата")
        self.assertEqual(payout.status, Payout.Status.PENDING)

        # Проверяем данные в ответе
        self.assertEqual(response.data["id"], payout.id)
        self.assertEqual(response.data["status"], Payout.Status.PENDING)


class PayoutCeleryTaskTest(TestCase):
    """ТЕСТ 2: Проверка вызова Celery-задачи"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("payouts-list")
        self.payload = {"amount": "777.00", "currency": "EUR", "recipient": "Alice"}

    @patch("payouts.views.process_payout.delay")
    def test_celery_task_called_on_create(self, mock_delay):
        """
        Проверяем, что при создании выплаты вызывается Celery задача
        через mock. Это изолированный тест проверки вызова задачи.
        """
        mock_delay.return_value = MagicMock(id="test-task-id")

        response = self.client.post(self.url, self.payload, format="json")

        # Проверяем успешное создание
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Celery задача была вызвана
        self.assertTrue(mock_delay.called)

        # задача вызвана с правильным аргументом (ID выплаты)
        payout = Payout.objects.first()
        mock_delay.assert_called_once_with(payout.id)

        # delay был вызван ровно один раз
        self.assertEqual(mock_delay.call_count, 1)

    @patch("payouts.views.process_payout.delay")
    def test_celery_task_not_called_on_invalid_data(self, mock_delay):
        """
        Дополнительный тест: задача не вызывается при ошибке валидации
        """
        invalid_payload = {"amount": "-100.00", "currency": "USD"}

        response = self.client.post(self.url, invalid_payload, format="json")

        # запрос не прошел
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Celery задача НЕ была вызвана
        self.assertFalse(mock_delay.called)

        # объект не создан
        self.assertEqual(Payout.objects.count(), 0)
