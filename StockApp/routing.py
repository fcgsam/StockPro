from django.urls import re_path
from .consumers import StockConsumer, IndexStockConsumer,OneStockConsumer

websocket_urlpatterns = [
    re_path(r'ws/stock/(?P<symbol>[^/]+)/$', StockConsumer.as_asgi()),
    re_path(r'ws/(?P<indexName>[^/]+)/$', IndexStockConsumer.as_asgi()),  # Changed to re_path with regex
    re_path(r'ws/stock/(?P<symbol>[^/]+)/$', OneStockConsumer.as_asgi()),
]
