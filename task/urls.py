from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from kolleno.views import ExchangeRateAPIView, URLInfoViewSet

router = DefaultRouter()
router.register(r"url-info", URLInfoViewSet)

api_urls = [path("exchange-rate", ExchangeRateAPIView.as_view(), name='exchange-rate')] + router.urls
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
]
