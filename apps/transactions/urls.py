from rest_framework.routers import DefaultRouter

from apps.transactions.views import TransactionViewSet

router = DefaultRouter()
router.register(prefix="", viewset=TransactionViewSet, basename="transactions")
urlpatterns = router.urls
