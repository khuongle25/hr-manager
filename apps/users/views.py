from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
from .serializers import UserSerializer, UserRegisterSerializer
from .permissions import IsHRUser, IsOwnerOrHR, IsTeamLeadUser
from rest_framework import generics
from rest_framework import serializers
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsTeamLeadUser]  # Cho phép HR và Team Lead
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'hr':
            return User.objects.all()
        elif user.role == 'team_lead':
            # Team Lead thấy tất cả nhân viên thuộc các phòng ban mình quản lý (dựa vào members)
            lead_departments = user.lead_departments.all()
            return User.objects.filter(departments__in=lead_departments).distinct()
        else:
            return User.objects.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

# Đã vô hiệu hóa API đăng ký tự do. Chỉ HR mới được tạo user qua giao diện quản lý nhân sự.

class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
