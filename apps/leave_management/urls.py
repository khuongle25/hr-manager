from rest_framework.routers import DefaultRouter
from .views import LeaveRequestViewSet, LeaveTypeViewSet, LeaveBalanceViewSet

router = DefaultRouter()
router.register(r'leave-requests', LeaveRequestViewSet, basename='leaverequest')
router.register(r'leave-types', LeaveTypeViewSet, basename='leavetype')
router.register(r'leave-balances', LeaveBalanceViewSet, basename='leavebalance')

urlpatterns = router.urls