from rest_framework import serializers
from .models import User
import secrets
from apps.departments.models import Department
from apps.departments.serializers import DepartmentSerializer

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), source='department', write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'employee_id', 'phone', 'address', 'date_of_birth', 'hire_date', 
            'department', 'department_id', 'password'
        ] 
        extra_kwargs = {'password': {'write_only': True}}
        
    # Quy ước: Nếu bạn đặt tên trường là abc_xyz = serializers.SerializerMethodField(), DRF sẽ tìm hàm get_abc_xyz(self, obj).
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def get_department(self, obj):
        if obj.department:
            return DepartmentSerializer(obj.department).data
        return None
    
    def validate_email(self, value):
        # Kiểm tra email trùng lặp, nhưng cho phép cập nhật chính mình
        instance = getattr(self, 'instance', None)
        # Loại bỏ user có id bằng với instance.id (nếu đang cập nhật một user đã tồn tại). Nếu không có instance (tức là đang tạo mới), thì không loại bỏ gì cả.
        if User.objects.filter(email=value).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError("Email đã tồn tại")
        return value
    
    def validate_username(self, value):
        # Kiểm tra username trùng lặp, nhưng cho phép cập nhật chính mình
        instance = getattr(self, 'instance', None)
        if User.objects.filter(username=value).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError("Username đã tồn tại")
        return value
    
    def update(self, instance, validated_data):
        department = validated_data.pop('department', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        # Đồng bộ members
        if department is not None:
            instance.department = department
            instance.save()
            if department:
                department.members.add(instance)
                department.save()
        return instance

    def create(self, validated_data):
        department = validated_data.pop('department', None)
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_password(secrets.token_urlsafe(12))
        user.is_active = True
        if department:
            user.department = department
        user.save()
        # Đồng bộ members
        if department:
            department.members.add(user)
            department.save()
        # Nếu là team_lead và có department, thêm vào danh sách lead của phòng ban
        if user.role == 'team_lead' and department:
            department.lead.add(user)
            department.save()
        return user

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']  # KHÔNG có employee_id
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Sinh employee_id tự động (ví dụ: EMP + số thứ tự)
        last_user = User.objects.order_by('-id').first()
        next_id = (last_user.id + 1) if last_user else 1
        employee_id = f"EMP{next_id:05d}"

        user = User.objects.create_user(
            employee_id=employee_id,
            **validated_data
        )
        user.is_active = True
        user.save()
        return user