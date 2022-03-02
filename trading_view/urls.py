from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter('api')
router.register(r'Strategy', views.StrategyViewSet)
router.register(r'trade/by', views.TradeByViewSet, basename="Stockinfo")
router.register(r'trade/all', views.TradeAllViewSet, basename="Stockinfo")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', views.data),
    path('api/', include(router.urls)),
    path('api/stock/all/', views.StockAllViewSet),
]
