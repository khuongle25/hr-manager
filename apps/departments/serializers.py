from rest_framework import serializers
from .models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    lead = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    lead_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    lead_email = serializers.EmailField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'lead', 'lead_id', 'lead_email', 'members', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        lead_id = validated_data.pop('lead_id', None)
        lead_email = validated_data.pop('lead_email', None)
        department = Department.objects.create(**validated_data)
        from apps.users.models import User
        if lead_email:
            try:
                lead_user = User.objects.get(email=lead_email)
                if lead_user.role != 'team_lead':
                    lead_user.role = 'team_lead'
                    lead_user.save()
                old_departments = lead_user.lead_departments.exclude(id=department.id)
                for old_dept in old_departments:
                    old_dept.lead.remove(lead_user)
                    old_dept.save()
                department.lead.add(lead_user)
                department.save()
                lead_user.department = department
                lead_user.save()
            except User.DoesNotExist:
                pass
        elif lead_id:
            try:
                lead_user = User.objects.get(id=lead_id)
                if lead_user.role != 'team_lead':
                    lead_user.role = 'team_lead'
                    lead_user.save()
                old_departments = lead_user.lead_departments.exclude(id=department.id)
                for old_dept in old_departments:
                    old_dept.lead.remove(lead_user)
                    old_dept.save()
                department.lead.add(lead_user)
                department.save()
                lead_user.department = department
                lead_user.save()
            except User.DoesNotExist:
                pass
        return department
        
    def update(self, instance, validated_data):
        lead_id = validated_data.pop('lead_id', None)
        lead_email = validated_data.pop('lead_email', None)
        from apps.users.models import User
        lead_user = None
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if lead_email:
            try:
                lead_user = User.objects.get(email=lead_email)
                if lead_user.role != 'team_lead':
                    lead_user.role = 'team_lead'
                    lead_user.save()
                old_departments = lead_user.lead_departments.exclude(id=instance.id)
                for old_dept in old_departments:
                    old_dept.lead.remove(lead_user)
                    old_dept.save()
                if not instance.lead.filter(id=lead_user.id).exists():
                    instance.lead.add(lead_user)
                instance.save()
                lead_user.department = instance
                lead_user.save()
            except User.DoesNotExist:
                pass
        elif lead_id is not None:
            try:
                if lead_id:
                    lead_user = User.objects.get(id=lead_id)
                    if lead_user.role != 'team_lead':
                        lead_user.role = 'team_lead'
                        lead_user.save()
                    old_departments = lead_user.lead_departments.exclude(id=instance.id)
                    for old_dept in old_departments:
                        old_dept.lead.remove(lead_user)
                        old_dept.save()
                    if not instance.lead.filter(id=lead_user.id).exists():
                        instance.lead.add(lead_user)
                    lead_user.department = instance
                    lead_user.save()
            except User.DoesNotExist:
                pass
        instance.save()
        return instance
        
    def validate_name(self, value):
        instance = getattr(self, 'instance', None)
        qs = Department.objects.filter(name=value)
        if instance is not None:
            qs = qs.exclude(id=instance.id)
        if qs.exists():
            raise serializers.ValidationError("Tên phòng ban đã tồn tại")
        return value

    def get_lead(self, obj):
        return [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": f"{u.first_name} {u.last_name}"
            }
            for u in obj.lead.all()
        ]

    def get_members(self, obj):
        return [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": f"{u.first_name} {u.last_name}"
            }
            for u in obj.members.all()
        ]
        
        