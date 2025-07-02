from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet, UserMeView
from django.urls import path

router = DefaultRouter()
router.register(r'users', UserViewSet)
urlpatterns = [
    path('me/', UserMeView.as_view(), name='user-me'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += router.urls