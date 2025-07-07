from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Department
from .serializers import DepartmentSerializer
from apps.users.permissions import IsHRUser, IsTeamLeadUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from apps.users.models import User
from django.core.cache import cache

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsTeamLeadUser]  # ⭐ Cho phép HR và Team Lead đọc
    
    def get_permissions(self):
        """Override permission cho từng action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'assign_lead']:
            # Chỉ HR mới được tạo/sửa/xóa
            permission_classes = [IsAuthenticated, IsHRUser]
        else:
            # Team Lead được đọc danh sách departments
            permission_classes = [IsAuthenticated, IsTeamLeadUser]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'hr':
            return Department.objects.all()
        elif user.role == 'team_lead':
            # Team Lead chỉ thấy phòng ban mình quản lý
            return Department.objects.filter(lead=user)
        else:
            # Employee chỉ thấy phòng ban mình thuộc về
            return Department.objects.filter(members=user)
    
    def list(self, request, *args, **kwargs):
        user = request.user
        if user.role == 'hr':
            cache_key = 'departments_list_hr'
            data = cache.get(cache_key)
            if data is not None:
                print('CACHE HIT')
                return Response(data)
            print('CACHE MISS')
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, timeout=300)
            return response
        # Team lead/employee không cache (vì dữ liệu cá nhân hóa)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()
        cache.delete('departments_list_hr')
        
    def perform_update(self, serializer):
        serializer.save()
        cache.delete('departments_list_hr')

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete('departments_list_hr')

    @action(detail=True, methods=['post'], url_path='assign-lead')
    def assign_lead(self, request, pk=None):
        department = self.get_object()
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        # Nếu user chưa phải team lead thì cập nhật role
        if user.role != 'team_lead':
            user.role = 'team_lead'
            user.save()
        # Nếu user đang là lead phòng ban khác, xóa khỏi lead phòng ban cũ
        old_departments = user.lead_departments.exclude(id=department.id)
        for old_dept in old_departments:
            old_dept.lead.remove(user)
            old_dept.save()
        # Thêm user vào danh sách lead của phòng ban này nếu chưa có
        if not department.lead.filter(id=user.id).exists():
            department.lead.add(user)
        department.save()
        # Nếu user không thuộc phòng ban này thì chuyển họ sang phòng ban này
        if hasattr(user, 'department') and user.department != department:
            user.department = department
            user.save()
        return Response({'success': f'{user.email} đã được bổ nhiệm làm lead phòng ban.'})