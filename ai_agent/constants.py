"""
Constants cho HR Management System
"""

# Department mappings
DEPARTMENT_MAPPINGS = {
    "it": 1,
    "công nghệ thông tin": 1,
    "technology": 1,
    "hr": 2,
    "nhân sự": 2,
    "human resource": 2,
    "accounting": 3,
    "kế toán": 3,
    "tài chính": 3,
    "marketing": 4,
    "tiếp thị": 4,
    "sales": 5,
    "bán hàng": 5,
}

# Leave type mappings
LEAVE_TYPE_MAPPINGS = {
    "annual": 1,
    "nghỉ phép năm": 1,
    "phép năm": 1,
    "sick": 2,
    "nghỉ ốm": 2,
    "ốm đau": 2,
    "ốm": 2,  # ⭐ THÊM mapping này
    "personal": 3,
    "cá nhân": 3,
    "việc riêng": 3,
    "maternity": 4,
    "thai sản": 4,
    "đẻ": 4,
}

# Role mappings
ROLE_MAPPINGS = {
    "nhân viên": "employee",
    "nhan vien": "employee",
    "employee": "employee",
    "trưởng phòng": "team_lead",
    "truong phong": "team_lead",
    "team lead": "team_lead",
    "team_lead": "team_lead",
    "hr": "hr",
    "nhân sự": "hr",
    "nhan su": "hr",
}

# Status mappings
STATUS_MAPPINGS = {
    "chờ duyệt": "pending",
    "cho duyet": "pending",
    "pending": "pending",
    "đã duyệt": "approved", 
    "da duyet": "approved",
    "approved": "approved",
    "duyệt": "approved",
    "duyet": "approved",
    "từ chối": "denied",
    "tu choi": "denied",
    "denied": "denied",
    "bị từ chối": "denied",
}

# Common Vietnamese to English field mappings
FIELD_MAPPINGS = {
    "ho_ten": "full_name",
    "họ_tên": "full_name",
    "ten": "first_name",
    "tên": "first_name", 
    "ho": "last_name",
    "họ": "last_name",
    "email": "email",
    "mat_khau": "password",
    "mật_khẩu": "password",
    "vai_tro": "role",
    "vai_trò": "role",
    "phong_ban": "department_id",
    "phòng_ban": "department_id",
    "ma_nhan_vien": "employee_id",
    "mã_nhân_viên": "employee_id",
    "dien_thoai": "phone",
    "điện_thoại": "phone",
    "dia_chi": "address",
    "địa_chỉ": "address",
    "ngay_sinh": "date_of_birth",
    "ngày_sinh": "date_of_birth",
    "ngay_vao_lam": "hire_date",
    "ngày_vào_làm": "hire_date",
    "loai_nghi_phep": "leave_type_id",
    "loại_nghỉ_phép": "leave_type_id",
    "ngay_bat_dau": "start_date",
    "ngày_bắt_đầu": "start_date",
    "ngay_ket_thuc": "end_date", 
    "ngày_kết_thúc": "end_date",
    "ly_do": "reason",
    "lý_do": "reason",
    "trang_thai": "status",
    "trạng_thái": "status",
}