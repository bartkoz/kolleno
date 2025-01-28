from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from .models import URLInfo
from .serializers import URLInfoSerializer, URLPostSerializer
from .services import ExchangeRateException, ExchangeRateService


class URLInfoViewSetTests(APITestCase):
    def setUp(self):
        self.url_info = baker.make(URLInfo)
        self.list_url = reverse("urlinfo-list")
        self.detail_url = reverse("urlinfo-detail", kwargs={"pk": self.url_info.pk})

    def test_list_url_info(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_url_info(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["url"], self.url_info.url)

    @patch("kolleno.views.requests.get")
    def test_create_url_info(self, mock_get):
        mock_response = Mock()
        mock_response.content = (
            b'<html><title>Test Title</title><img src="test.jpg"/></html>'
        )
        mock_get.return_value = mock_response

        data = {"url": "https://example.com"}
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(URLInfo.objects.count(), 2)
        self.assertEqual(response.data["domain_name"], "example.com")

    def test_create_invalid_url(self):
        data = {"url": "invalid-url"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class URLInfoSerializerTests(TestCase):
    def test_url_info_serializer(self):
        url_info = baker.make(URLInfo)
        serializer = URLInfoSerializer(url_info)
        self.assertIn("url", serializer.data)
        self.assertIn("domain_name", serializer.data)
        self.assertIn("protocol", serializer.data)

    def test_url_post_serializer_valid(self):
        data = {"url": "https://example.com"}
        serializer = URLPostSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_url_post_serializer_invalid(self):
        data = {"url": "invalid-url"}
        serializer = URLPostSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class ExchangeRateServiceTests(TestCase):
    def setUp(self):
        self.service = ExchangeRateService()

    @patch("kolleno.services.requests.get")
    def test_get_bitcoin_price_in_eur(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"EUR": {"15m": 50000.0}}
        mock_get.return_value = mock_response

        price = self.service._get_bitcoin_price_in_eur()
        self.assertEqual(price, 50000.0)

    @patch("kolleno.services.requests.get")
    def test_get_eur_to_gbp_rate(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "dataSets": [{"series": {"0:0:0:0:0": {"observations": {"0": [0.85]}}}}]
        }
        mock_get.return_value = mock_response

        rate = self.service._get_eur_to_gbp_rate_from_ecb()
        self.assertEqual(rate, 0.85)

    @patch.object(ExchangeRateService, "_get_bitcoin_price_in_eur")
    @patch.object(ExchangeRateService, "_get_eur_to_gbp_rate_from_ecb")
    def test_get_exchange_data(self, mock_gbp_rate, mock_btc_price):
        mock_btc_price.return_value = 50000.0
        mock_gbp_rate.return_value = 0.85

        data = self.service.get_exchange_data()

        self.assertEqual(data["bitcoin_eur"], 50000.0)
        self.assertEqual(data["eur_to_gbp"], 0.85)
        self.assertEqual(data["bitcoin_gbp"], 42500.0)

    @patch("kolleno.services.requests.get")
    def test_bitcoin_price_error_handling(self, mock_get):
        mock_get.side_effect = Exception()

        with self.assertRaises(ExchangeRateException):
            self.service._get_bitcoin_price_in_eur()


class ExchangeRateAPIViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("exchange-rate")

    @patch.object(ExchangeRateService, "get_exchange_data")
    def test_get_exchange_rates(self, mock_get_data):
        expected_data = {
            "bitcoin_eur": 50000.0,
            "eur_to_gbp": 0.85,
            "bitcoin_gbp": 42500.0,
        }
        mock_get_data.return_value = expected_data

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
