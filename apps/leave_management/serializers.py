from rest_framework import serializers
from .models import LeaveType, LeaveRequest, LeaveBalance
from apps.users.serializers import UserSerializer
from apps.departments.serializers import DepartmentSerializer
from datetime import datetime
from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, fields

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'
        
class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    leave_type = LeaveTypeSerializer(read_only=True)
    leave_type_id = serializers.PrimaryKeyRelatedField(
        queryset=LeaveType.objects.all(), 
        source='leave_type', 
        write_only=True,
        required=False
    )
    approver = UserSerializer(read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        
    def get_duration(self, obj):
        return (obj.end_date - obj.start_date).days + 1
    
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        leave_type = data.get('leave_type')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise serializers.ValidationError("Ngày bắt đầu phải trước ngày kết thúc")
            
            if start_date < datetime.now().date():
                raise serializers.ValidationError("Ngày bắt đầu không được trước ngày hiện tại")
        
        return data
    
    '''
    self.context là một dictionary mà DRF truyền vào mỗi serializer khi khởi tạo.
    Khi bạn dùng viewset hoặc APIView, DRF sẽ tự động truyền context này, trong đó thường có key 'request' (là đối tượng request hiện tại).
    Mục đích:
    Cho phép bạn truy cập thông tin request (user, method, data, v.v.) trong serializer, ví dụ để gán user, kiểm tra quyền, hoặc custom logic theo request.
    '''
    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        
        if user.role == 'employee':
            validated_data['employee'] = user
        elif user.role == 'team_lead':
            validated_data['department'] = user.department
        elif user.role == 'hr':
            validated_data['employee'] = user
            validated_data['approver'] = user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        request = self.context['request']
        user = request.user
        
        if user.role == 'team_lead':
            if instance.department != user.department:
                raise serializers.ValidationError("Bạn không có quyền cập nhật đơn nghỉ phép của phòng khác")
    
class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee = UserSerializer(read_only=True)
    leave_type = LeaveTypeSerializer(read_only=True)
    leave_type_id = serializers.PrimaryKeyRelatedField(
        queryset=LeaveType.objects.all(), 
        source='leave_type', 
        write_only=True,
        required=False
    )
    used = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveBalance
        fields = '__all__'
    
    def get_used(self, obj):
        """Tính số ngày đã sử dụng"""
        approved_requests = LeaveRequest.objects.filter(
            employee=obj.employee,
            leave_type=obj.leave_type,
            status='approved'
        )
        
        total_days = 0
        for request in approved_requests:
            days = (request.end_date - request.start_date).days + 1
            total_days += days
        
        return total_days
    
    def get_remaining(self, obj):
        """Tính số ngày còn lại"""
        used = self.get_used(obj)
        return obj.balance - used
    
    def create(self, validated_data):
        """Tạo LeaveBalance với employee được set từ view"""
        request = self.context.get('request')
        if request and '_employee' in self.context:
            validated_data['employee'] = self.context['_employee']
        return super().create(validated_data)