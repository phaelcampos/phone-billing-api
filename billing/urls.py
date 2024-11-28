from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CallRecordViewSet, PhoneBillView

router = DefaultRouter()
router.register(r'call-records', CallRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('phone-bills/<str:phone>/', PhoneBillView.as_view(), name='phone-bill'),
]
