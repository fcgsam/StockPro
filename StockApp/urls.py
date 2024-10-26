from django.urls import path,include
from .views import *
urlpatterns = [
    path("",StockListPage,name="home"),
    path('all_stock/', all_stocks, name='all_stock'),
    path('stock/<str:symbol>/', stock_detail, name='stock_detail'),
    # path('index/<str:index_symbol>/', index_detail, name='index_detail'),
    path('stock/<str:symbol>/<str:period>/', stock_history_dynamic, name='stock_history_dynamic'),
    path('load-more-stocks/', load_more_stocks, name='load_more_stocks'),

]
