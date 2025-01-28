from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import URLInfo
from .serializers import URLInfoSerializer, URLPostSerializer
from .services import ExchangeRateService


class URLInfoViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
    queryset = URLInfo.objects.all()
    serializer_class = URLInfoSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return URLPostSerializer
        return URLInfoSerializer

    def create(self, request, *args, **kwargs):
        serializer = URLPostSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data["url"]

            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "html.parser")
                parsed_url = urlparse(url)
                domain_name = parsed_url.netloc
                protocol = parsed_url.scheme
                title = soup.title.string if soup.title else None
                images = [img["src"] for img in soup.find_all("img", src=True)]
                stylesheets_count = len(soup.find_all("link", rel="stylesheet"))

                url_info = URLInfo.objects.create(
                    url=url,
                    domain_name=domain_name,
                    protocol=protocol,
                    title=title,
                    images=images,
                    stylesheets_count=stylesheets_count,
                )
                return Response(
                    URLInfoSerializer(url_info).data, status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExchangeRateAPIView(APIView):

    def get(self, request, *args, **kwargs):
        return Response(ExchangeRateService().get_exchange_data())
