"""
Schema Registry for HR Management System
Định nghĩa đầy đủ các API endpoints, parameters, và validation rules
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, date
import re
from constants import FIELD_MAPPINGS, DEPARTMENT_MAPPINGS, LEAVE_TYPE_MAPPINGS, ROLE_MAPPINGS, STATUS_MAPPINGS

@dataclass
class PermissionRule:
    """Định nghĩa rule permission chi tiết"""
    allowed_roles: List[str]  # Danh sách roles được phép
    object_level_check: Optional[str] = None  # Logic check object-level
    description: str = ""

@dataclass
class FieldSchema:
    """Định nghĩa schema cho một field"""
    name: str
    type: str  # "string", "integer", "date", "email", "phone", "choice"
    required: bool = False
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    choices: Optional[List[str]] = None
    pattern: Optional[str] = None
    description: str = ""
    example: Optional[str] = None

@dataclass
class APIEndpoint:
    """Định nghĩa schema cho một API endpoint"""
    name: str
    method: str  # GET, POST, PUT, DELETE
    url_pattern: str
    fields: List[FieldSchema]
    required_role: Optional[str] = None
    description: str = ""
    example_request: Optional[Dict] = None
    example_response: Optional[Dict] = None

class SchemaRegistry:
    def __init__(self):
        self.endpoints = self._init_endpoints()
        self.field_mappings = FIELD_MAPPINGS
        # self.validation_rules = self._init_validation_rules()
        
        # Mapping constants
        self.department_mappings = DEPARTMENT_MAPPINGS
        self.leave_type_mappings = LEAVE_TYPE_MAPPINGS
        self.role_mappings = ROLE_MAPPINGS
        self.status_mappings = STATUS_MAPPINGS
        
        # ⭐ New permission system
        self.permission_rules = self._init_permission_rules()
        
    def _init_endpoints(self) -> Dict[str, APIEndpoint]:
        """Định nghĩa tất cả API endpoints"""
        return {
            # === LEAVE MANAGEMENT ===
            "request_leave": APIEndpoint(
                name="request_leave",
                method="POST",
                url_pattern="/api/leave-requests/",
                description="Tạo đơn nghỉ phép mới",
                fields=[
                    FieldSchema("leave_type_id", "integer", required=True, description="ID loại nghỉ phép"),
                    FieldSchema("start_date", "date", required=True, description="Ngày bắt đầu nghỉ"),
                    FieldSchema("end_date", "date", required=True, description="Ngày kết thúc nghỉ"),
                    FieldSchema("reason", "string", required=False, description="Lý do nghỉ phép")
                ]
            ),
            
            "approve_leave": APIEndpoint(
                name="approve_leave",
                method="POST",
                url_pattern="/api/leave-requests/{leave_request_id}/approve/",
                description="Duyệt đơn nghỉ phép",
                fields=[
                    FieldSchema("leave_request_id", "integer", required=True, description="ID đơn nghỉ phép")
                ]
            ),
            
            "deny_leave": APIEndpoint(
                name="deny_leave",
                method="POST",
                url_pattern="/api/leave-requests/{leave_request_id}/deny/",
                description="Từ chối đơn nghỉ phép",
                fields=[
                    FieldSchema("leave_request_id", "integer", required=True, description="ID đơn nghỉ phép")
                ]
            ),
            
            "view_leave_history": APIEndpoint(
                name="view_leave_history",
                method="GET",
                url_pattern="/api/leave-requests/",
                description="Xem lịch sử đơn nghỉ phép",
                fields=[
                    FieldSchema("user_id", "integer", required=False, description="ID nhân viên (optional)"),
                    FieldSchema("status", "string", required=False, description="Trạng thái đơn")
                ]
            ),
            
            "pending_leave_requests": APIEndpoint(
                name="pending_leave_requests",
                method="GET",
                url_pattern="/api/leave-requests/",
                description="Xem các đơn chờ duyệt",
                fields=[
                    FieldSchema("status", "string", required=False, description="pending")
                ]
            ),
            
            "view_leave_balance": APIEndpoint(
                name="view_leave_balance",
                method="GET",
                url_pattern="/api/leave-balances/",
                description="Xem số ngày phép còn lại",
                fields=[
                    FieldSchema("employee_id", "integer", required=False, description="ID nhân viên")
                ]
            ),
            
            "update_leave_balance": APIEndpoint(
                name="update_leave_balance",
                method="PUT",
                url_pattern="/api/leave-balances/{id}/",
                description="Cập nhật số ngày phép",
                fields=[
                    FieldSchema("id", "integer", required=True, description="ID leave balance"),
                    FieldSchema("balance", "integer", required=True, description="Số ngày phép mới")
                ]
            ),
            
            "change_leave_decision": APIEndpoint(
                name="change_leave_decision",
                method="POST",
                url_pattern="/api/leave-requests/{leave_request_id}/change_decision/",
                description="Thay đổi quyết định duyệt/từ chối đơn nghỉ phép",
                fields=[
                    FieldSchema("leave_request_id", "integer", required=True, description="ID đơn nghỉ phép"),
                    FieldSchema("status", "string", required=True, description="Quyết định mới (approved/denied)")
                ]
            ),
            
            # === EMPLOYEE MANAGEMENT ===
            "add_employee": APIEndpoint(
                name="add_employee",
                method="POST",
                url_pattern="/api/users/",
                description="Thêm nhân viên mới",
                fields=[
                    FieldSchema("username", "string", required=True, description="Tên đăng nhập"),
                    FieldSchema("email", "email", required=True, description="Email nhân viên"),
                    FieldSchema("first_name", "string", required=True, description="Tên"),
                    FieldSchema("last_name", "string", required=True, description="Họ"),
                    FieldSchema("password", "string", required=True, description="Mật khẩu"),
                    FieldSchema("role", "string", required=False, description="Vai trò"),
                    FieldSchema("department_id", "integer", required=False, description="ID phòng ban"),
                    FieldSchema("employee_id", "string", required=False, description="Mã nhân viên"),
                    FieldSchema("phone", "string", required=False, description="Số điện thoại"),
                    FieldSchema("address", "string", required=False, description="Địa chỉ"),
                    FieldSchema("date_of_birth", "date", required=False, description="Ngày sinh"),
                    FieldSchema("hire_date", "date", required=False, description="Ngày vào làm")
                ]
            ),
            
            "update_employee": APIEndpoint(
                name="update_employee",
                method="PUT",
                url_pattern="/api/users/{user_id}/",
                description="Cập nhật thông tin nhân viên",
                fields=[
                    FieldSchema("user_id", "integer", required=True, description="ID nhân viên"),
                    FieldSchema("email", "email", required=False, description="Email"),
                    FieldSchema("first_name", "string", required=False, description="Tên"),
                    FieldSchema("last_name", "string", required=False, description="Họ"),
                    FieldSchema("role", "string", required=False, description="Vai trò"),
                    FieldSchema("department_id", "integer", required=False, description="ID phòng ban"),
                    FieldSchema("phone", "string", required=False, description="Số điện thoại"),
                    FieldSchema("address", "string", required=False, description="Địa chỉ")
                ]
            ),
            
            "delete_employee": APIEndpoint(
                name="delete_employee",
                method="DELETE",
                url_pattern="/api/users/{user_id}/",
                description="Xóa nhân viên",
                fields=[
                    FieldSchema("user_id", "integer", required=True, description="ID nhân viên")
                ]
            ),
            
            "list_employees": APIEndpoint(
                name="list_employees",
                method="GET",
                url_pattern="/api/users/",
                description="Xem danh sách nhân viên",
                fields=[
                    FieldSchema("department_id", "integer", required=False, description="Filter theo phòng ban"),
                    FieldSchema("role", "string", required=False, description="Filter theo vai trò")
                ]
            ),
            
            "search_employees": APIEndpoint(
                name="search_employees",
                method="GET",
                url_pattern="/api/users/",
                description="Tìm kiếm nhân viên",
                fields=[
                    FieldSchema("search", "string", required=False, description="Từ khóa tìm kiếm"),
                    FieldSchema("full_name", "string", required=False, description="Tên đầy đủ")
                ]
            ),
            
            "view_employee_details": APIEndpoint(
                name="view_employee_details",
                method="GET",
                url_pattern="/api/users/{user_id}/",
                description="Xem chi tiết nhân viên",
                fields=[
                    FieldSchema("user_id", "integer", required=True, description="ID nhân viên")
                ]
            ),
            
            # === DEPARTMENT MANAGEMENT ===
            "add_department": APIEndpoint(
                name="add_department",
                method="POST",
                url_pattern="/api/departments/",
                description="Thêm phòng ban mới",
                fields=[
                    FieldSchema("name", "string", required=True, description="Tên phòng ban"),
                    FieldSchema("description", "string", required=False, description="Mô tả phòng ban"),
                    FieldSchema("lead_email", "email", required=False, description="Email trưởng phòng")
                ]
            ),
            
            "update_department": APIEndpoint(
                name="update_department",
                method="PUT",
                url_pattern="/api/departments/{department_id}/",
                description="Cập nhật thông tin phòng ban",
                fields=[
                    FieldSchema("department_id", "integer", required=True, description="ID phòng ban"),
                    FieldSchema("name", "string", required=False, description="Tên phòng ban"),
                    FieldSchema("description", "string", required=False, description="Mô tả phòng ban")
                ]
            ),
            
            "delete_department": APIEndpoint(
                name="delete_department",
                method="DELETE",
                url_pattern="/api/departments/{department_id}/",
                description="Xóa phòng ban",
                fields=[
                    FieldSchema("department_id", "integer", required=True, description="ID phòng ban")
                ]
            ),
            
            "list_departments": APIEndpoint(
                name="list_departments",
                method="GET",
                url_pattern="/api/departments/",
                description="Xem danh sách phòng ban",
                fields=[]
            ),
            
            "assign_department_lead": APIEndpoint(
                name="assign_department_lead",
                method="POST",
                url_pattern="/api/departments/{department_id}/assign-lead/",
                description="Bổ nhiệm trưởng phòng",
                fields=[
                    FieldSchema("department_id", "integer", required=True, description="ID phòng ban"),
                    FieldSchema("email", "email", required=True, description="Email nhân viên được bổ nhiệm")
                ]
            ),
            
            # === LEAVE TYPE MANAGEMENT ===
            "view_leave_types": APIEndpoint(
                name="view_leave_types",
                method="GET",
                url_pattern="/api/leave-types/",
                description="Xem danh sách loại nghỉ phép",
                fields=[]
            ),
            
            "add_leave_type": APIEndpoint(
                name="add_leave_type",
                method="POST",
                url_pattern="/api/leave-types/",
                description="Thêm loại nghỉ phép mới",
                fields=[
                    FieldSchema("name", "string", required=True, description="Tên loại nghỉ phép"),
                    FieldSchema("description", "string", required=False, description="Mô tả"),
                    FieldSchema("max_days_per_year", "integer", required=False, description="Số ngày tối đa/năm")
                ]
            ),
            
            "update_leave_type": APIEndpoint(
                name="update_leave_type",
                method="PUT",
                url_pattern="/api/leave-types/{leave_type_id}/",
                description="Cập nhật loại nghỉ phép",
                fields=[
                    FieldSchema("leave_type_id", "integer", required=True, description="ID loại nghỉ phép"),
                    FieldSchema("name", "string", required=False, description="Tên loại nghỉ phép"),
                    FieldSchema("description", "string", required=False, description="Mô tả"),
                    FieldSchema("max_days_per_year", "integer", required=False, description="Số ngày tối đa/năm")
                ]
            ),
            
            "delete_leave_type": APIEndpoint(
                name="delete_leave_type",
                method="DELETE",
                url_pattern="/api/leave-types/{leave_type_id}/",
                description="Xóa loại nghỉ phép",
                fields=[
                    FieldSchema("leave_type_id", "integer", required=True, description="ID loại nghỉ phép")
                ]
            ),
            
            # === PROFILE ===
            "view_profile": APIEndpoint(
                name="view_profile",
                method="GET",
                url_pattern="/api/me/",
                description="Xem thông tin cá nhân",
                fields=[]
            ),
        }
    
    def _init_permission_rules(self) -> Dict[str, PermissionRule]:
        """Định nghĩa chi tiết permission rules"""
        return {
            # === LEAVE MANAGEMENT ===
            "request_leave": PermissionRule(
                allowed_roles=["employee", "team_lead", "hr"],
                description="Mọi user đều có thể tạo đơn nghỉ phép"
            ),
            
            "approve_leave": PermissionRule(
                allowed_roles=["team_lead", "hr"],
                object_level_check="team_member_or_hr",
                description="Team Lead chỉ approve đơn của team member, HR approve tất cả"
            ),
            
            "deny_leave": PermissionRule(
                allowed_roles=["team_lead", "hr"], 
                object_level_check="team_member_or_hr",
                description="Team Lead chỉ deny đơn của team member, HR deny tất cả"
            ),
            
            "view_leave_history": PermissionRule(
                allowed_roles=["employee", "team_lead", "hr"],
                object_level_check="own_or_team_or_hr",
                description="Employee xem của mình, Team Lead xem team, HR xem tất cả"
            ),
            
            "pending_leave_requests": PermissionRule(
                allowed_roles=["team_lead", "hr"],
                object_level_check="team_or_hr",
                description="Team Lead xem đơn chờ của team, HR xem tất cả"
            ),
            
            "view_leave_balance": PermissionRule(
                allowed_roles=["employee", "team_lead", "hr"],
                object_level_check="own_or_team_or_hr",
                description="Employee xem của mình, Team Lead xem team, HR xem tất cả"
            ),
            
            "update_leave_balance": PermissionRule(
                allowed_roles=["hr"],
                description="Chỉ HR mới được cập nhật leave balance"
            ),
            
            "change_leave_decision": PermissionRule(
                allowed_roles=["team_lead", "hr"],
                object_level_check="team_member_or_hr",
                description="Team Lead chỉ được thay đổi quyết định đơn nghỉ phép của team member, HR approve tất cả"
            ),
            
            # === EMPLOYEE MANAGEMENT ===
            "add_employee": PermissionRule(
                allowed_roles=["hr"],
                description="Chỉ HR mới được thêm nhân viên"
            ),
            
            "update_employee": PermissionRule(
                allowed_roles=["hr"],
                description="Chỉ HR mới được cập nhật thông tin nhân viên"
            ),
            
            "delete_employee": PermissionRule(
                allowed_roles=["hr"], 
                description="Chỉ HR mới được xóa nhân viên"
            ),
            
            "list_employees": PermissionRule(
                allowed_roles=["team_lead", "hr"],
                object_level_check="team_or_hr",
                description="Team Lead xem team member, HR xem tất cả"
            ),
            
            "search_employees": PermissionRule(
                allowed_roles=["team_lead", "hr"],
                object_level_check="team_or_hr", 
                description="Team Lead search trong team, HR search tất cả"
            ),
            
            "view_employee_details": PermissionRule(
                allowed_roles=["employee", "team_lead", "hr"],
                object_level_check="own_or_team_or_hr",
                description="Employee xem của mình, Team Lead xem team, HR xem tất cả"
            ),
            
            # === DEPARTMENT MANAGEMENT ===
            "add_department": PermissionRule(
                allowed_roles=["hr"],
                description="Chỉ HR mới được thêm phòng ban"
            ),
            
            "update_department": PermissionRule(
                allowed_roles=["hr"],
                description="Chỉ HR mới được cập nhật phòng ban"
            ),
            
            "delete_department": PermissionRule(
                allowed_roles=["hr"],
                description="Chỉ HR mới được xóa phòng ban"
            ),
            
            "list_departments": PermissionRule(
                allowed_roles=["employee", "team_lead", "hr"],
                description="Tất cả user đều có thể xem danh sách phòng ban"
            ),
            
            "assign_department_lead": PermissionRule(
                allowed_roles=["hr"],
                description="Chỉ HR mới được bổ nhiệm trưởng phòng"
            ),
            
            # === LEAVE TYPE MANAGEMENT ===
            "view_leave_types": PermissionRule(
                allowed_roles=["employee", "team_lead", "hr"],
                description="Tất cả user đều có thể xem danh sách loại nghỉ phép"
            ),
            
            "add_leave_type": PermissionRule(
                allowed_roles=["hr"],
                description="Chỉ HR mới được thêm loại nghỉ phép"
            ),
            
            "update_leave_type": PermissionRule(
                allowed_roles=["hr"],
                description="Chỉ HR mới được cập nhật loại nghỉ phép"
            ),
            
            "delete_leave_type": PermissionRule(
                allowed_roles=["hr"],
                description="Chỉ HR mới được xóa loại nghỉ phép"
            ),
            
            # === PROFILE ===
            "view_profile": PermissionRule(
                allowed_roles=["employee", "team_lead", "hr"],
                description="Tất cả user đều có thể xem profile của mình"
            ),
        }
    def get_endpoint(self, intent: str) -> Optional[APIEndpoint]:
        """Lấy endpoint definition cho intent"""
        return self.endpoints.get(intent)
    
    def validate_entities(self, intent: str, entities: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate entities theo schema của intent"""
        endpoint = self.get_endpoint(intent)
        if not endpoint:
            return False, [f"Intent '{intent}' không tồn tại"]
        
        errors = []
        for field in endpoint.fields:
            if field.required and field.name not in entities:
                errors.append(f"Thiếu thông tin bắt buộc: {field.description or field.name}")
            
            if field.name in entities:
                value = entities[field.name]
                # Validate type
                if field.type == "integer" and not isinstance(value, int):
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        errors.append(f"{field.description or field.name} phải là số nguyên")
                
                elif field.type == "email" and value:
                    import re
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, str(value)):
                        errors.append(f"{field.description or field.name} không đúng định dạng email")
                
                elif field.type == "date" and value:
                    try:
                        from datetime import datetime
                        if isinstance(value, str):
                            datetime.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        errors.append(f"{field.description or field.name} phải có định dạng YYYY-MM-DD")
        
        return len(errors) == 0, errors
    
    def get_required_fields(self, intent: str) -> List[str]:
        """Lấy danh sách required fields cho intent"""
        endpoint = self.get_endpoint(intent)
        if not endpoint:
            return []
        
        return [field.name for field in endpoint.fields if field.required]
    
    def get_field_description(self, intent: str, field_name: str) -> str:
        """Lấy description của field"""
        endpoint = self.get_endpoint(intent)
        if not endpoint:
            return field_name
        
        for field in endpoint.fields:
            if field.name == field_name:
                return field.description or field_name
        
        return field_name
    
    def map_vietnamese_fields(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Map các field tiếng Việt sang tiếng Anh"""
        mapped = {}
        for key, value in entities.items():
            english_key = self.field_mappings.get(key, key)
            mapped[english_key] = value
        return mapped
    
    def map_department_name_to_id(self, department_name: str) -> Optional[int]:
        """Map tên phòng ban sang ID"""
        normalized_name = department_name.lower().strip()
        return self.department_mappings.get(normalized_name)
    
    def map_leave_type_name_to_id(self, leave_type_name: str) -> Optional[int]:
        """Map tên loại nghỉ phép sang ID"""
        normalized_name = leave_type_name.lower().strip()
        return self.leave_type_mappings.get(normalized_name)
    
    def map_role_vietnamese_to_english(self, role_vn: str) -> str:
        """Map vai trò tiếng Việt sang tiếng Anh"""
        normalized_role = role_vn.lower().strip()
        return self.role_mappings.get(normalized_role, role_vn)
    
    def map_status_vietnamese_to_english(self, status_vn: str) -> str:
        """Map trạng thái tiếng Việt sang tiếng Anh"""
        normalized_status = status_vn.lower().strip()
        return self.status_mappings.get(normalized_status, status_vn)
    
    def get_permission_rule(self, intent: str) -> Optional[PermissionRule]:
        """Lấy permission rule cho intent"""
        return self.permission_rules.get(intent)
    
    def requires_object_level_check(self, intent: str) -> bool:
        """Kiểm tra xem intent có cần object-level permission không"""
        rule = self.permission_rules.get(intent)
        return rule and rule.object_level_check is not None
    
    def check_role_permission(self, intent: str, user_role: str) -> bool:
        """Kiểm tra quyền thực hiện intent - CHỈ VIEW LEVEL"""
        permission_rule = self.permission_rules.get(intent)
        if not permission_rule:
            return False
        
        return user_role in permission_rule.allowed_roles
    
    def get_permission_rule(self, intent: str) -> Optional[PermissionRule]:
        """Lấy permission rule cho intent"""
        return self.permission_rules.get(intent)
    
    def requires_object_level_check(self, intent: str) -> bool:
        """Kiểm tra xem intent có cần object-level permission không"""
        rule = self.permission_rules.get(intent)
        return rule and rule.object_level_check is not None

# Singleton instance
schema_registry = SchemaRegistry()