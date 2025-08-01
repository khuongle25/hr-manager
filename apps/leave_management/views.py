from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LeaveRequest, LeaveType, LeaveBalance
from .serializers import LeaveRequestSerializer, LeaveTypeSerializer, LeaveBalanceSerializer
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, BasePermission
from apps.users.permissions import IsHRUser, IsTeamLeadUser, IsOwnerOrHR
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

class IsHROrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'hr'

class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'hr':
            return LeaveRequest.objects.all()
        elif user.role == 'team_lead':
            # Team Lead thấy tất cả đơn của nhân viên thuộc các phòng ban mình quản lý (dựa vào members)
            lead_departments = user.lead_departments.all()
            return LeaveRequest.objects.filter(employee__departments__in=lead_departments).distinct()
        else:
            # Employee chỉ thấy đơn của mình
            return LeaveRequest.objects.filter(employee=user)

    def perform_create(self, serializer):
        # Tự động set employee là user hiện tại
        serializer.save(employee=self.request.user)

    def _calculate_leave_days(self, leave):
        """Tính số ngày nghỉ"""
        return (leave.end_date - leave.start_date).days + 1

    def _update_leave_balance(self, leave, action='subtract'):
        """Cập nhật ngày phép"""
        try:
            balance = LeaveBalance.objects.get(employee=leave.employee, leave_type=leave.leave_type)
            num_days = self._calculate_leave_days(leave)
            
            if action == 'subtract':
                balance.balance -= num_days
            elif action == 'add':
                balance.balance += num_days
            
            balance.save()
            return True
        except LeaveBalance.DoesNotExist:
            return False

    def _needs_both_approvals(self, leave):
        """
        Kiểm tra xem đơn nghỉ phép có cần cả Team Lead và HR duyệt không
        - Nếu employee là Team Lead → chỉ cần HR duyệt
        - Nếu employee là Employee thường → cần cả Team Lead và HR duyệt
        """
        return leave.employee.role != 'team_lead'

    def _is_fully_approved(self, leave):
        """Kiểm tra xem đơn đã được duyệt đầy đủ chưa"""
        if self._needs_both_approvals(leave):
            # Employee thường: cần cả team_lead và hr approved
            return leave.team_lead_status == 'approved' and leave.hr_status == 'approved'
        else:
            # Team Lead: chỉ cần hr approved
            return leave.hr_status == 'approved'

    def _is_denied(self, leave):
        """Kiểm tra xem đơn có bị từ chối không"""
        if self._needs_both_approvals(leave):
            # Employee thường: một trong hai từ chối là denied
            return leave.team_lead_status == 'denied' or leave.hr_status == 'denied'
        else:
            # Team Lead: chỉ xét hr_status
            return leave.hr_status == 'denied'

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        user = request.user
        
        # Kiểm tra quyền duyệt
        if user.role not in ['hr', 'team_lead']:
            return Response({'detail': 'Bạn không có quyền duyệt đơn.'}, status=403)
        
        # ⭐ NGĂN TEAM LEAD TỰ DUYỆT ĐƠN CỦA MÌNH
        if user.role == 'team_lead' and leave.employee == user:
            return Response({'detail': 'Bạn không thể tự duyệt đơn nghỉ phép của chính mình.'}, status=403)
        
        # Team Lead chỉ duyệt được đơn của nhân viên trong team
        if user.role == 'team_lead' and not leave.employee.departments.filter(lead=user).exists():
            return Response({'detail': 'Bạn chỉ có thể duyệt đơn của nhân viên trong team.'}, status=403)
        
        # Nếu đã duyệt rồi thì không làm gì
        if (user.role == 'team_lead' and leave.team_lead_status == 'approved') or (user.role == 'hr' and leave.hr_status == 'approved'):
            return Response({'detail': 'Bạn đã duyệt đơn này trước đó.'}, status=400)
        
        # Cập nhật trạng thái duyệt riêng
        if user.role == 'team_lead':
            leave.team_lead_status = 'approved'
        if user.role == 'hr':
            leave.hr_status = 'approved'
        
        # ⭐ SỬ DỤNG HELPER METHOD ĐỂ KIỂM TRA APPROVAL
        if self._is_fully_approved(leave):
            # Kiểm tra đủ ngày phép không (chỉ khi chuyển từ pending)
            num_days = self._calculate_leave_days(leave)
            try:
                balance = LeaveBalance.objects.get(employee=leave.employee, leave_type=leave.leave_type)
                if balance.balance < num_days:
                    return Response({'detail': f'Không đủ ngày phép. Còn lại: {balance.balance} ngày.'}, status=400)
            except LeaveBalance.DoesNotExist:
                return Response({'detail': 'Không tìm thấy LeaveBalance cho nhân viên này.'}, status=400)
            
            if leave.status == 'pending':
                if not self._update_leave_balance(leave, 'subtract'):
                    return Response({'detail': 'Lỗi khi cập nhật ngày phép.'}, status=400)
            
            leave.status = 'approved'
            leave.approver = user
        
        leave.save()
        
        # Thông báo động dựa trên role của employee
        if leave.employee.role == 'team_lead':
            status_msg = f'Đã duyệt đơn Team Lead. HR: {leave.hr_status}, Tổng: {leave.status}'
        else:
            status_msg = f'Đã duyệt đơn. Team Lead: {leave.team_lead_status}, HR: {leave.hr_status}, Tổng: {leave.status}'
        
        return Response({'status': status_msg})

    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        leave = self.get_object()
        user = request.user
        # Kiểm tra quyền từ chối
        if user.role not in ['hr', 'team_lead']:
            return Response({'detail': 'Bạn không có quyền từ chối đơn.'}, status=403)
        
        # ⭐ NGĂN TEAM LEAD TỰ TỪ CHỐI ĐƠN CỦA MÌNH
        if user.role == 'team_lead' and leave.employee == user:
            return Response({'detail': 'Bạn không thể tự từ chối đơn nghỉ phép của chính mình.'}, status=403)
        
        # Team Lead chỉ từ chối được đơn của nhân viên trong team
        if user.role == 'team_lead' and not leave.employee.departments.filter(lead=user).exists():
            return Response({'detail': 'Bạn chỉ có thể từ chối đơn của nhân viên trong team.'}, status=403)
        
        # Nếu đã từ chối rồi thì không làm gì
        if (user.role == 'team_lead' and leave.team_lead_status == 'denied') or (user.role == 'hr' and leave.hr_status == 'denied'):
            return Response({'detail': 'Bạn đã từ chối đơn này trước đó.'}, status=400)
        
        # Cập nhật trạng thái từ chối riêng
        if user.role == 'team_lead':
            leave.team_lead_status = 'denied'
        if user.role == 'hr':
            leave.hr_status = 'denied'
        
        # ⭐ SỬ DỤNG HELPER METHOD ĐỂ KIỂM TRA DENIAL
        if self._is_denied(leave):
            if leave.status == 'approved':
                if not self._update_leave_balance(leave, 'add'):
                    return Response({'detail': 'Lỗi khi hoàn lại ngày phép.'}, status=400)
            leave.status = 'denied'
            leave.approver = user
        
        leave.save()
        
        # Thông báo động dựa trên role của employee
        if leave.employee.role == 'team_lead':
            status_msg = f'Đã từ chối đơn Team Lead. HR: {leave.hr_status}, Tổng: {leave.status}'
        else:
            status_msg = f'Đã từ chối đơn. Team Lead: {leave.team_lead_status}, HR: {leave.hr_status}, Tổng: {leave.status}'
        
        return Response({'status': status_msg})

    @action(detail=True, methods=['post'])
    def change_decision(self, request, pk=None):
        """Thay đổi quyết định đã duyệt/từ chối"""
        leave = self.get_object()
        user = request.user
        new_status = request.data.get('status')
        
        # Kiểm tra quyền
        if user.role not in ['hr', 'team_lead']:
            return Response({'detail': 'Bạn không có quyền thay đổi quyết định.'}, status=403)
        
        # ⭐ NGĂN TEAM LEAD TỰ THAY ĐỔI ĐƠN CỦA MÌNH
        if user.role == 'team_lead' and leave.employee == user:
            return Response({'detail': 'Bạn không thể tự thay đổi quyết định đơn nghỉ phép của chính mình.'}, status=403)
        
        if user.role == 'team_lead' and not leave.employee.departments.filter(lead=user).exists():
            return Response({'detail': 'Bạn chỉ có thể thay đổi đơn của nhân viên trong team.'}, status=403)
        
        if new_status not in ['approved', 'denied']:
            return Response({'detail': 'Trạng thái không hợp lệ.'}, status=400)
        
        # Cập nhật trạng thái riêng
        if user.role == 'team_lead':
            leave.team_lead_status = new_status
        if user.role == 'hr':
            leave.hr_status = new_status
        
        # ⭐ SỬ DỤNG HELPER METHODS ĐỂ XÁC ĐỊNH TRẠNG THÁI TỔNG HỢP
        if self._is_denied(leave):
            if leave.status == 'approved':
                if not self._update_leave_balance(leave, 'add'):
                    return Response({'detail': 'Lỗi khi hoàn lại ngày phép.'}, status=400)
            leave.status = 'denied'
            leave.approver = user
        elif self._is_fully_approved(leave):
            # Kiểm tra đủ ngày phép không (chỉ khi chuyển từ pending)
            num_days = self._calculate_leave_days(leave)
            try:
                balance = LeaveBalance.objects.get(employee=leave.employee, leave_type=leave.leave_type)
                if balance.balance < num_days:
                    return Response({'detail': f'Không đủ ngày phép. Còn lại: {balance.balance} ngày.'}, status=400)
            except LeaveBalance.DoesNotExist:
                return Response({'detail': 'Không tìm thấy LeaveBalance cho nhân viên này.'}, status=400)
            
            if leave.status == 'pending':
                if not self._update_leave_balance(leave, 'subtract'):
                    return Response({'detail': 'Lỗi khi cập nhật ngày phép.'}, status=400)
            leave.status = 'approved'
            leave.approver = user
        else:
            leave.status = 'pending'
            leave.approver = None
        
        leave.save()
        
        # Thông báo động dựa trên role của employee
        if leave.employee.role == 'team_lead':
            status_msg = f'Đã thay đổi quyết định Team Lead. HR: {leave.hr_status}, Tổng: {leave.status}'
        else:
            status_msg = f'Đã thay đổi quyết định. Team Lead: {leave.team_lead_status}, HR: {leave.hr_status}, Tổng: {leave.status}'
        
        return Response({'status': status_msg})
    
class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsHROrReadOnly]

class LeaveBalanceViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'hr':
            return LeaveBalance.objects.all()
        elif user.role == 'team_lead':
            # Team Lead thấy tất cả balance của nhân viên thuộc các phòng ban mình quản lý (dựa vào members)
            lead_departments = user.lead_departments.all()
            return LeaveBalance.objects.filter(employee__departments__in=lead_departments).distinct()
        else:
            # Employee chỉ thấy balance của mình
            return LeaveBalance.objects.filter(employee=user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        # Chỉ cho phép HR tạo LeaveBalance
        if self.action == 'create':
            user = self.request.user
            if user.role != 'hr':
                from rest_framework import serializers
                raise serializers.ValidationError("Chỉ HR mới được tạo LeaveBalance!")
            employee_id = self.request.data.get('employee')
            if employee_id:
                from apps.users.models import User
                try:
                    employee = User.objects.get(id=employee_id)
                    context['_employee'] = employee
                except User.DoesNotExist:
                    raise serializers.ValidationError("Không tìm thấy nhân viên")
        return context
    
    def create(self, request, *args, **kwargs):
        """Override create để xử lý trường hợp đã tồn tại"""
        # Kiểm tra xem đã tồn tại LeaveBalance cho employee và leave_type này chưa
        employee_id = request.data.get('employee')
        leave_type_id = request.data.get('leave_type_id')
        
        if employee_id and leave_type_id:
            try:
                from apps.users.models import User
                from .models import LeaveType
                
                # Chuyển đổi string thành integer
                employee_id = int(employee_id)
                leave_type_id = int(leave_type_id)
                
                employee = User.objects.get(id=employee_id)
                leave_type = LeaveType.objects.get(id=leave_type_id)
                
                # Kiểm tra quyền
                user = request.user
                if user.role == 'team_lead' and employee.department.lead != user:
                    raise serializers.ValidationError("Bạn chỉ có thể tạo ngày phép cho nhân viên trong team")
                
                # Kiểm tra xem đã tồn tại chưa
                existing_balance = LeaveBalance.objects.filter(
                    employee=employee,
                    leave_type=leave_type
                ).first()
                
                if existing_balance:
                    # Cập nhật balance hiện có
                    new_balance = int(request.data.get('balance', 0))
                    existing_balance.balance = new_balance
                    existing_balance.save()
                    
                    serializer = self.get_serializer(existing_balance)
                    return Response(serializer.data, status=200)
                    
            except (User.DoesNotExist, LeaveType.DoesNotExist, ValueError):
                pass
        
        # Nếu không tồn tại hoặc có lỗi, tạo mới như bình thường
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.user.role != 'hr':
            raise PermissionDenied("Chỉ HR mới được cập nhật LeaveBalance!")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if request.user.role != 'hr':
            raise PermissionDenied("Chỉ HR mới được cập nhật LeaveBalance!")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'hr':
            raise PermissionDenied("Chỉ HR mới được xóa LeaveBalance!")
        return super().destroy(request, *args, **kwargs)