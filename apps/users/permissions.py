from rest_framework.permissions import BasePermission

class IsHRUser(BasePermission):
    """
    Chỉ cho phép HR truy cập
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'hr'

class IsTeamLeadUser(BasePermission):
    """
    Cho phép HR và Team Lead truy cập
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['hr', 'team_lead']

class IsOwnerOrHR(BasePermission):
    """
    Cho phép chủ sở hữu hoặc HR truy cập
    """
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'hr' or obj.employee == request.user

class IsOwnerOrTeamLead(BasePermission):
    """
    Cho phép chủ sở hữu, Team Lead hoặc HR truy cập
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'hr':
            return True
        if request.user.role == 'team_lead':
            return obj.employee.departments.filter(lead=request.user).exists()
        return obj.employee == request.user 