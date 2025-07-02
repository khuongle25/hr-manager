#!/usr/bin/env python
"""
Script tạo dữ liệu mẫu cho hệ thống HR
Chạy: python create_sample_data.py
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_management.settings')
django.setup()

from apps.users.models import User
from apps.departments.models import Department
from apps.leave_management.models import LeaveType, LeaveRequest, LeaveBalance

def create_sample_data():
    print("Đang tạo dữ liệu mẫu...")
    
    # Tạo phòng ban
    departments = [
        {'name': 'Phòng Kỹ thuật', 'description': 'Phòng phát triển sản phẩm'},
        {'name': 'Phòng Kinh doanh', 'description': 'Phòng bán hàng và marketing'},
        {'name': 'Phòng Nhân sự', 'description': 'Phòng quản lý nhân sự'},
        {'name': 'Phòng Tài chính', 'description': 'Phòng kế toán và tài chính'},
    ]
    
    created_departments = []
    for dept_data in departments:
        dept, created = Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={'description': dept_data['description']}
        )
        created_departments.append(dept)
        if created:
            print(f"Đã tạo phòng ban: {dept.name}")
    
    # Tạo loại nghỉ phép
    leave_types = [
        {'name': 'Nghỉ phép năm', 'max_days_per_year': 12, 'description': 'Nghỉ phép theo quy định'},
        {'name': 'Nghỉ ốm', 'max_days_per_year': 5, 'description': 'Nghỉ khi bị ốm'},
        {'name': 'Nghỉ việc riêng', 'max_days_per_year': 3, 'description': 'Nghỉ việc cá nhân'},
        {'name': 'Nghỉ thai sản', 'max_days_per_year': 180, 'description': 'Nghỉ thai sản'},
    ]
    
    created_leave_types = []
    for lt_data in leave_types:
        lt, created = LeaveType.objects.get_or_create(
            name=lt_data['name'],
            defaults={
                'max_days_per_year': lt_data['max_days_per_year'],
                'description': lt_data['description']
            }
        )
        created_leave_types.append(lt)
        if created:
            print(f"Đã tạo loại nghỉ phép: {lt.name}")
    
    # Tạo users mẫu
    users_data = [
        # HR Manager
        {
            'username': 'hr_manager',
            'email': 'hr@company.com',
            'password': 'password123',
            'first_name': 'Nguyễn',
            'last_name': 'Văn HR',
            'role': 'hr',
            'department': created_departments[2],  # Phòng Nhân sự
            'phone': '0901234567',
            'address': 'Hà Nội'
        },
        # Team Lead - Kỹ thuật
        {
            'username': 'tech_lead',
            'email': 'tech.lead@company.com',
            'password': 'password123',
            'first_name': 'Trần',
            'last_name': 'Thị Tech',
            'role': 'team_lead',
            'department': created_departments[0],  # Phòng Kỹ thuật
            'phone': '0901234568',
            'address': 'Hà Nội'
        },
        # Team Lead - Kinh doanh
        {
            'username': 'sales_lead',
            'email': 'sales.lead@company.com',
            'password': 'password123',
            'first_name': 'Lê',
            'last_name': 'Văn Sales',
            'role': 'team_lead',
            'department': created_departments[1],  # Phòng Kinh doanh
            'phone': '0901234569',
            'address': 'Hà Nội'
        },
        # Employees
        {
            'username': 'dev1',
            'email': 'dev1@company.com',
            'password': 'password123',
            'first_name': 'Phạm',
            'last_name': 'Văn Dev',
            'role': 'employee',
            'department': created_departments[0],  # Phòng Kỹ thuật
            'phone': '0901234570',
            'address': 'Hà Nội'
        },
        {
            'username': 'dev2',
            'email': 'dev2@company.com',
            'password': 'password123',
            'first_name': 'Hoàng',
            'last_name': 'Thị Dev',
            'role': 'employee',
            'department': created_departments[0],  # Phòng Kỹ thuật
            'phone': '0901234571',
            'address': 'Hà Nội'
        },
        {
            'username': 'sales1',
            'email': 'sales1@company.com',
            'password': 'password123',
            'first_name': 'Vũ',
            'last_name': 'Văn Sales',
            'role': 'employee',
            'department': created_departments[1],  # Phòng Kinh doanh
            'phone': '0901234572',
            'address': 'Hà Nội'
        },
        {
            'username': 'accountant',
            'email': 'accountant@company.com',
            'password': 'password123',
            'first_name': 'Đặng',
            'last_name': 'Thị Kế',
            'role': 'employee',
            'department': created_departments[3],  # Phòng Tài chính
            'phone': '0901234573',
            'address': 'Hà Nội'
        },
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
                'department': user_data['department'],
                'phone': user_data['phone'],
                'address': user_data['address'],
                'hire_date': date.today() - timedelta(days=365)
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            created_users.append(user)
            print(f"Đã tạo user: {user.get_full_name()} ({user.role})")
    
    # Tạo Leave Balance cho tất cả employees
    employees = [u for u in created_users if u.role == 'employee']
    for employee in employees:
        for leave_type in created_leave_types:
            balance, created = LeaveBalance.objects.get_or_create(
                employee=employee,
                leave_type=leave_type,
                defaults={'balance': leave_type.max_days_per_year}
            )
            if created:
                print(f"Đã tạo Leave Balance cho {employee.get_full_name()}: {leave_type.name} - {balance.balance} ngày")
    
    # Tạo một số đơn nghỉ phép mẫu
    sample_requests = [
        {
            'employee': next(u for u in employees if u.username == 'dev1'),
            'leave_type': next(lt for lt in created_leave_types if lt.name == 'Nghỉ phép năm'),
            'start_date': date.today() + timedelta(days=7),
            'end_date': date.today() + timedelta(days=9),
            'reason': 'Nghỉ phép gia đình',
            'status': 'pending'
        },
        {
            'employee': next(u for u in employees if u.username == 'sales1'),
            'leave_type': next(lt for lt in created_leave_types if lt.name == 'Nghỉ ốm'),
            'start_date': date.today() - timedelta(days=2),
            'end_date': date.today() - timedelta(days=1),
            'reason': 'Bị cảm cúm',
            'status': 'approved'
        },
        {
            'employee': next(u for u in employees if u.username == 'dev2'),
            'leave_type': next(lt for lt in created_leave_types if lt.name == 'Nghỉ việc riêng'),
            'start_date': date.today() + timedelta(days=15),
            'end_date': date.today() + timedelta(days=15),
            'reason': 'Đi khám bệnh',
            'status': 'pending'
        },
    ]
    
    for req_data in sample_requests:
        request, created = LeaveRequest.objects.get_or_create(
            employee=req_data['employee'],
            leave_type=req_data['leave_type'],
            start_date=req_data['start_date'],
            end_date=req_data['end_date'],
            defaults={
                'reason': req_data['reason'],
                'status': req_data['status']
            }
        )
        if created:
            print(f"Đã tạo đơn nghỉ phép: {request.employee.get_full_name()} - {request.leave_type.name}")
    
    print("\n=== DỮ LIỆU MẪU ĐÃ ĐƯỢC TẠO ===")
    print(f"- {len(created_departments)} phòng ban")
    print(f"- {len(created_leave_types)} loại nghỉ phép")
    print(f"- {len(created_users)} users")
    print(f"- {LeaveBalance.objects.count()} leave balances")
    print(f"- {LeaveRequest.objects.count()} đơn nghỉ phép")
    
    print("\n=== THÔNG TIN ĐĂNG NHẬP ===")
    print("HR Manager: hr_manager / password123")
    print("Tech Lead: tech_lead / password123")
    print("Sales Lead: sales_lead / password123")
    print("Dev 1: dev1 / password123")
    print("Dev 2: dev2 / password123")
    print("Sales 1: sales1 / password123")
    print("Accountant: accountant / password123")

def create_leave_balances():
    """Tạo dữ liệu mẫu cho LeaveBalance"""
    from apps.leave_management.models import LeaveBalance, LeaveType
    from apps.users.models import User
    
    # Lấy tất cả user và leave type
    users = User.objects.all()
    leave_types = LeaveType.objects.all()
    
    for user in users:
        for leave_type in leave_types:
            # Tạo balance cho mỗi user với mỗi loại nghỉ phép
            balance, created = LeaveBalance.objects.get_or_create(
                employee=user,
                leave_type=leave_type,
                defaults={
                    'balance': 12 if leave_type.name == 'Nghỉ phép năm' else 5,
                }
            )
            if created:
                print(f"Đã tạo LeaveBalance cho {user.username} - {leave_type.name}")

if __name__ == "__main__":
    create_sample_data()
    print("Đã tạo xong dữ liệu mẫu!") 