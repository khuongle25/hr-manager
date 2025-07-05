import requests
import json
import re
import unicodedata

API_BASE = "http://localhost:8000/api"

# Danh sách intent tiếng Anh
INTENT_LIST = [
    "request_leave", "approve_leave", "deny_leave", "view_leave_balance", "view_leave_history", "pending_leave_requests",
    "add_employee", "add_department", "assign_department_lead", "view_profile", "list_employees", "list_departments", "update_leave_balance", "change_leave_decision",
    "delete_employee", "update_employee", "delete_department", "update_department", "view_employee_details", "search_employees",
    "view_leave_types", "add_leave_type", "update_leave_type", "delete_leave_type", "view_leave_statistics", "export_leave_data"
]
INTENT_MAPPING = {
    "xin_nghi_phep": "request_leave",
    "duyet_don": "approve_leave",
    "tu_choi_don": "deny_leave",
    "xem_ngay_phep": "view_leave_balance",
    "lich_su_nghi_phep": "view_leave_history",
    "danh_sach_don_cho_duyet": "pending_leave_requests",
    "them_nhan_vien": "add_employee",
    "them_phong_ban": "add_department",
    "bo_nhiem_truong_phong": "assign_department_lead",
    "thong_tin_ca_nhan": "view_profile",
    "danh_sach_nhan_vien": "list_employees",
    "danh_sach_phong_ban": "list_departments",
    "cap_nhat_ngay_phep": "update_leave_balance",
    "thay_doi_quyet_dinh": "change_leave_decision",
    "xoa_nhan_vien": "delete_employee",
    "cap_nhat_nhan_vien": "update_employee",
    "xoa_phong_ban": "delete_department",
    "cap_nhat_phong_ban": "update_department",
    "chi_tiet_nhan_vien": "view_employee_details",
    "tim_kiem_nhan_vien": "search_employees",
    "danh_sach_loai_nghi_phep": "view_leave_types",
    "them_loai_nghi_phep": "add_leave_type",
    "cap_nhat_loai_nghi_phep": "update_leave_type",
    "xoa_loai_nghi_phep": "delete_leave_type",
    "thong_ke_nghi_phep": "view_leave_statistics",
    "xuat_du_lieu_nghi_phep": "export_leave_data"
}

# Function registry: mô tả các intent, trường bắt buộc, trường tự động lấy
FUNCTION_REGISTRY = [
    {
        "name": "add_employee",
        "description": "Thêm nhân viên mới vào hệ thống",
        "required_fields": ["full_name", "email", "department_id"],
        "auto_fields": ["role"],
    },
    {
        "name": "request_leave",
        "description": "Tạo đơn xin nghỉ phép",
        "required_fields": ["leave_type_id", "start_date", "end_date", "reason"],
        "auto_fields": ["user_id"],
    },
    {
        "name": "approve_leave",
        "description": "Duyệt đơn xin nghỉ phép",
        "required_fields": ["leave_request_id"],
        "auto_fields": ["user_id"],
    },
    {
        "name": "deny_leave",
        "description": "Từ chối đơn xin nghỉ phép",
        "required_fields": ["leave_request_id"],
        "auto_fields": ["user_id"],
    },
    {
        "name": "view_leave_balance",
        "description": "Xem số ngày nghỉ phép còn lại",
        "required_fields": [],
        "auto_fields": ["user_id"],
    },
    {
        "name": "view_leave_history",
        "description": "Xem lịch sử đơn nghỉ phép",
        "required_fields": [],
        "auto_fields": ["user_id"],
    },
    {
        "name": "pending_leave_requests",
        "description": "Xem danh sách đơn nghỉ phép đang chờ duyệt",
        "required_fields": [],
        "auto_fields": ["user_id"],
    },
    {
        "name": "add_department",
        "description": "Thêm phòng ban mới",
        "required_fields": ["name"],
        "auto_fields": [],
    },
    {
        "name": "assign_department_lead",
        "description": "Bổ nhiệm trưởng phòng ban",
        "required_fields": ["department_id", "email"],
        "auto_fields": [],
    },
    {
        "name": "view_profile",
        "description": "Xem thông tin cá nhân",
        "required_fields": [],
        "auto_fields": ["user_id"],
    },
    {
        "name": "list_employees",
        "description": "Xem danh sách nhân viên trong phòng ban",
        "required_fields": ["department_id"],
        "auto_fields": [],
    },
    {
        "name": "list_departments",
        "description": "Xem danh sách tất cả phòng ban",
        "required_fields": [],
        "auto_fields": [],
    },
    {
        "name": "update_leave_balance",
        "description": "Cập nhật số ngày nghỉ phép của nhân viên",
        "required_fields": ["leave_balance_id", "balance"],
        "auto_fields": [],
    },
    {
        "name": "change_leave_decision",
        "description": "Thay đổi quyết định về đơn nghỉ phép",
        "required_fields": ["leave_request_id", "status"],
        "auto_fields": [],
    },
    {
        "name": "delete_employee",
        "description": "Xóa nhân viên khỏi hệ thống",
        "required_fields": ["user_id"],
        "auto_fields": [],
    },
    {
        "name": "update_employee",
        "description": "Cập nhật thông tin nhân viên",
        "required_fields": ["user_id"],
        "auto_fields": [],
    },
    {
        "name": "delete_department",
        "description": "Xóa phòng ban",
        "required_fields": ["department_id"],
        "auto_fields": [],
    },
    {
        "name": "update_department",
        "description": "Cập nhật thông tin phòng ban",
        "required_fields": ["department_id"],
        "auto_fields": [],
    },
    {
        "name": "view_employee_details",
        "description": "Xem chi tiết thông tin nhân viên",
        "required_fields": ["user_id"],
        "auto_fields": [],
    },
    {
        "name": "search_employees",
        "description": "Tìm kiếm nhân viên theo tiêu chí",
        "required_fields": [],
        "auto_fields": [],
    },
    {
        "name": "view_leave_types",
        "description": "Xem danh sách các loại nghỉ phép",
        "required_fields": [],
        "auto_fields": [],
    },
    {
        "name": "add_leave_type",
        "description": "Thêm loại nghỉ phép mới",
        "required_fields": ["name", "description"],
        "auto_fields": [],
    },
    {
        "name": "update_leave_type",
        "description": "Cập nhật loại nghỉ phép",
        "required_fields": ["leave_type_id"],
        "auto_fields": [],
    },
    {
        "name": "delete_leave_type",
        "description": "Xóa loại nghỉ phép",
        "required_fields": ["leave_type_id"],
        "auto_fields": [],
    },
    {
        "name": "view_leave_statistics",
        "description": "Xem thống kê nghỉ phép",
        "required_fields": [],
        "auto_fields": [],
    },
    {
        "name": "export_leave_data",
        "description": "Xuất dữ liệu nghỉ phép",
        "required_fields": [],
        "auto_fields": [],
    },
]

def check_missing_fields(intent, entities):
    func = next((f for f in FUNCTION_REGISTRY if f["name"] == intent), None)
    if not func:
        return []
    missing = []
    for field in func["required_fields"]:
        if field not in entities or not entities[field]:
            missing.append(field)
    return missing

def get_missing_fields_message(intent, missing_fields):
    """Tạo thông báo chi tiết về các trường còn thiếu"""
    field_descriptions = {
        "full_name": "họ tên nhân viên",
        "email": "email",
        "department_id": "ID phòng ban",
        "department_name": "tên phòng ban",
        "leave_type_id": "ID loại nghỉ phép",
        "start_date": "ngày bắt đầu",
        "end_date": "ngày kết thúc", 
        "reason": "lý do nghỉ phép",
        "leave_request_id": "ID đơn nghỉ phép",
        "name": "tên phòng ban",
        "description": "mô tả",
        "balance": "số ngày nghỉ phép",
        "leave_balance_id": "ID bảng nghỉ phép",
        "status": "trạng thái",
        "user_id": "ID nhân viên",
        "leave_type_id": "ID loại nghỉ phép",
        "search_term": "từ khóa tìm kiếm",
        "department_name": "tên phòng ban",
        "role": "vai trò",
        "phone": "số điện thoại",
        "address": "địa chỉ",
        "hire_date": "ngày thuê",
        "salary": "lương"
    }
    
    field_names = []
    for field in missing_fields:
        field_names.append(field_descriptions.get(field, field))
    
    return ", ".join(field_names)

def postprocess_intent(data):
    intent = data.get("intent")
    if intent not in INTENT_LIST:
        mapped_intent = INTENT_MAPPING.get(intent)
        if mapped_intent:
            data["intent"] = mapped_intent
        else:
            data["intent"] = "unknown"
    return data

def get_role_from_token(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{API_BASE}/me/", headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("role")
    except Exception as e:
        print("Error getting role from Django API:", e)
    return None

def get_department_id_by_name(department_name, token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{API_BASE}/departments/", headers=headers, timeout=5)
        if resp.status_code == 200:
            departments = resp.json()
            for dept in departments:
                if dept["name"].lower() == department_name.lower():
                    return dept["id"]
    except Exception as e:
        print("Error getting department id:", e)
    return None

def format_error_message(result, default_message="Có lỗi xảy ra. Vui lòng thử lại."):
    """Format thông báo lỗi từ response của API"""
    if not result:
        return default_message
    
    # Xử lý non_field_errors (lỗi chung)
    if "non_field_errors" in result:
        errors = result["non_field_errors"]
        return f"Lỗi: {'; '.join(errors)}"
    
    # Xử lý detail error
    if "detail" in result:
        return f"Lỗi: {result['detail']}"
    
    # Xử lý field-specific errors
    field_errors = []
    for field, error in result.items():
        if isinstance(error, list):
            field_errors.append(f"{field}: {error[0]}")
        else:
            field_errors.append(f"{field}: {error}")
    
    if field_errors:
        return f"Lỗi: {'; '.join(field_errors)}"
    
    return default_message

def validate_leave_dates(start_date, end_date):
    """Kiểm tra tính hợp lệ của ngày nghỉ phép"""
    from datetime import datetime, date
    
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        today = date.today()
        
        # Debug logging (đã bỏ để production)
        # print(f"DEBUG: start_date={start_date}, parsed_start={start}")
        # print(f"DEBUG: end_date={end_date}, parsed_end={end}")
        # print(f"DEBUG: today={today}")
        # print(f"DEBUG: start < today = {start < today}")
        
        if start < today:
            return False, f"Ngày bắt đầu ({start_date}) không được trước ngày hiện tại ({today}). Vui lòng chọn ngày trong tương lai."
        
        if end < start:
            return False, f"Ngày kết thúc ({end_date}) không được trước ngày bắt đầu ({start_date})"
        
        return True, None
    except ValueError:
        return False, "Định dạng ngày không hợp lệ (phải là YYYY-MM-DD)"

def normalize_text(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    return text.lower()

def get_user_id_by_name(full_name, token):
    """Tìm user_id theo tên đầy đủ (full_name), không dấu, không phân biệt hoa thường"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{API_BASE}/users/?search={full_name}", headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            norm_full_name = normalize_text(full_name)
            
            # Xử lý format response có "results" (paginated)
            if isinstance(data, dict) and "results" in data:
                users = data["results"]
            # Xử lý format response là list trực tiếp
            elif isinstance(data, list):
                users = data
            # Xử lý format response là dict đơn lẻ
            elif isinstance(data, dict) and "id" in data:
                users = [data]
            else:
                users = []
            
            print(f"DEBUG: Searching for '{full_name}' (normalized: '{norm_full_name}')")
            print(f"DEBUG: Found {len(users)} users")
            
            # Tìm user có full_name khớp chính xác
            for u in users:
                user_full_name = u.get("full_name", "")
                norm_user_name = normalize_text(user_full_name)
                print(f"DEBUG: Comparing '{norm_user_name}' with '{norm_full_name}'")
                if norm_user_name == norm_full_name:
                    print(f"DEBUG: Found exact match: {u['id']}")
                    return u["id"]
            
            # Nếu không tìm thấy khớp chính xác, trả về user đầu tiên
            if users:
                print(f"DEBUG: No exact match, returning first user: {users[0]['id']}")
                return users[0]["id"]
                
    except Exception as e:
        print("Error getting user id by name:", e)
    return None

def get_pending_leave_requests(user_id, token, start_date=None, end_date=None):
    """Tìm các đơn nghỉ phép chờ duyệt của user, có thể lọc theo khoảng ngày"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        # Lấy tất cả đơn và filter ở client-side vì backend có thể không filter đúng
        params = ""
        if start_date:
            params += f"start_date={start_date}"
        if end_date:
            params += f"&end_date={end_date}" if params else f"end_date={end_date}"
        
        url = f"{API_BASE}/leave-requests/"
        if params:
            url += f"?{params}"
            
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            # Xử lý format response
            if isinstance(data, dict) and "results" in data:
                all_requests = data["results"]
            elif isinstance(data, list):
                all_requests = data
            else:
                all_requests = []
            
            # Filter theo user_id, status = "pending", start_date, end_date
            filtered_requests = []
            for req in all_requests:
                employee = req.get("employee", {})
                employee_id = employee.get("id") if isinstance(employee, dict) else None
                
                # Nếu có user_id, chỉ lấy đơn của user đó
                if user_id and employee_id != user_id:
                    continue
                # Chỉ lấy đơn có status = "pending"
                if req.get("status") != "pending":
                    continue
                # Nếu có start_date, chỉ lấy đơn trùng khớp
                if start_date and req.get("start_date") != start_date:
                    continue
                # Nếu có end_date, chỉ lấy đơn trùng khớp
                if end_date and req.get("end_date") != end_date:
                    continue
                filtered_requests.append(req)
            
            print(f"DEBUG: Found {len(all_requests)} total requests, {len(filtered_requests)} pending for user {user_id} with date filter")
            for req in filtered_requests:
                employee_name = req['employee']['full_name'] if req.get('employee') else 'Unknown'
                print(f"DEBUG: Pending request ID {req['id']}, employee: {employee_name}, start: {req.get('start_date')}, end: {req.get('end_date')}")
            
            return filtered_requests
    except Exception as e:
        print("Error getting pending leave requests:", e)
    return []

# Mapping intent tiếng Anh sang API call

def call_api(intent, entities, user_token, user_role=None, user_message_input=None):
    # Map employee_name sang full_name nếu có
    if 'employee_name' in entities and 'full_name' not in entities:
        entities['full_name'] = entities['employee_name']
    
    # Nếu có trường 'decision' mà không có 'status', thì chuyển sang 'status'
    if 'decision' in entities and 'status' not in entities:
        entities['status'] = entities['decision']
    
    # Map status tiếng Việt sang tiếng Anh nếu có
    STATUS_MAP = {
        "duyệt": "approved",
        "approve": "approved",
        "từ chối": "denied",
        "deny": "denied",
        "chờ duyệt": "pending",
        "pending": "pending",
        "approved": "approved",
        "denied": "denied"
    }
    if 'status' in entities and entities['status']:
        status_val = str(entities['status']).strip().lower()
        if status_val in STATUS_MAP:
            entities['status'] = STATUS_MAP[status_val]
    
    headers = {"Authorization": f"Bearer {user_token}"}
    # Lấy role thực tế từ token
    role = get_role_from_token(user_token)
    # Kiểm tra thiếu thông tin trước khi gọi API
    missing_fields = check_missing_fields(intent, entities)
    # --- SMART APPROVE/DENY LEAVE LOGIC ---
    if intent in ["approve_leave", "deny_leave"] and ("leave_request_id" not in entities or not entities["leave_request_id"]):
        # Nếu có tên nhân viên hoặc khoảng ngày
        full_name = entities.get("full_name")
        start_date = entities.get("start_date")
        end_date = entities.get("end_date")
        if full_name:
            user_id = get_user_id_by_name(full_name, user_token)
            print("DEBUG user_id:", user_id)
            if not user_id:
                return {"result": {}, "user_message": f"Không tìm thấy nhân viên tên {full_name}."}
            pending_requests = get_pending_leave_requests(user_id, user_token, start_date, end_date)
            print("DEBUG pending_requests:", pending_requests)
            if not pending_requests:
                return {"result": {}, "user_message": f"Không có đơn nghỉ phép nào đang chờ duyệt của {full_name}."}
            if len(pending_requests) == 1:
                entities["leave_request_id"] = pending_requests[0]["id"]
                # Gọi lại chính intent với leave_request_id
                return call_api(intent, entities, user_token, user_role)
            elif len(pending_requests) > 1:
                msg = f"Có {len(pending_requests)} đơn chờ duyệt của {full_name}: " + \
                    ", ".join([f"ID {r['id']} từ {r['start_date']} đến {r['end_date']}" for r in pending_requests])
                return {"result": {}, "user_message": msg}
        elif start_date or end_date:
            pending_requests = get_pending_leave_requests(None, user_token, start_date, end_date)
            print("DEBUG pending_requests:", pending_requests)
            if not pending_requests:
                return {"result": {}, "user_message": "Không có đơn chờ duyệt nào trong khoảng ngày đã chọn."}
            if len(pending_requests) == 1:
                entities["leave_request_id"] = pending_requests[0]["id"]
                return call_api(intent, entities, user_token, user_role)
            elif len(pending_requests) > 1:
                msg = f"Có {len(pending_requests)} đơn chờ duyệt trong khoảng ngày đã chọn: " + \
                    ", ".join([f"ID {r['id']} của {r['employee']['full_name']} từ {r['start_date']} đến {r['end_date']}" for r in pending_requests])
                return {"result": {}, "user_message": msg}
    if missing_fields:
        # Sinh thông báo hỏi user bổ sung thông tin còn thiếu
        field_names = get_missing_fields_message(intent, missing_fields)
        return {
            "result": {},
            "user_message": f"Bạn cần cung cấp thêm thông tin: {field_names} để thực hiện chức năng này.",
        }
    # Các intent trả về dữ liệu, không tự sinh user_message nữa
    if intent in ["view_profile", "list_employees", "list_departments", "view_leave_balance", "view_leave_history", "pending_leave_requests", "view_employee_details", "search_employees", "view_leave_types", "view_leave_statistics", "export_leave_data"]:
        # Gọi API như cũ
        if intent == "view_profile":
            resp = requests.get(f"{API_BASE}/me/", headers=headers)
            result = resp.json()
            user_message = f"Name: {result.get('full_name', '')}, Email: {result.get('email', '')}, Role: {result.get('role', '')}."
            return {"result": result, "user_message": user_message}
        elif intent == "list_employees":
            dept_id = entities["department_id"]
            resp = requests.get(f"{API_BASE}/users/?department={dept_id}", headers=headers)
            result = resp.json()
            # Không tự sinh user_message, chỉ trả về dữ liệu
            return {"result": result, "user_message": user_message_input or ""}
        elif intent == "list_departments":
            resp = requests.get(f"{API_BASE}/departments/", headers=headers)
            result = resp.json()
            user_message = f"There are {len(result)} departments." if isinstance(result, list) else "No departments found."
            return {"result": result, "user_message": user_message}
        elif intent == "view_leave_balance":
            resp = requests.get(f"{API_BASE}/leave-balances/", headers=headers)
            result = resp.json()
            if isinstance(result, list) and result:
                days = result[0].get('balance', 0)
                user_message = f"Bạn còn {days} ngày nghỉ phép."
            else:
                user_message = "Không tìm thấy thông tin ngày nghỉ phép."
            return {"result": result, "user_message": user_message}
        elif intent == "view_leave_history":
            resp = requests.get(f"{API_BASE}/leave-requests/", headers=headers)
            result = resp.json()
            user_message = f"Bạn có {len(result)} đơn nghỉ phép." if isinstance(result, list) else "Không tìm thấy lịch sử nghỉ phép."
            return {"result": result, "user_message": user_message}
        elif intent == "pending_leave_requests":
            resp = requests.get(f"{API_BASE}/leave-requests/?status=pending", headers=headers)
            result = resp.json()
            user_message = f"Có {len(result)} đơn nghỉ phép đang chờ duyệt." if isinstance(result, list) else "Không có đơn nghỉ phép nào đang chờ duyệt."
            return {"result": result, "user_message": user_message}
        elif intent == "view_employee_details":
            user_id = entities["user_id"]
            resp = requests.get(f"{API_BASE}/users/{user_id}/", headers=headers)
            result = resp.json()
            if resp.status_code < 400:
                user_message = f"Employee: {result.get('full_name', '')}, Email: {result.get('email', '')}, Department: {result.get('department', '')}"
            else:
                user_message = result.get('detail', 'Error getting employee details.')
            return {"result": result, "user_message": user_message}
        elif intent == "search_employees":
            params = {k: v for k, v in entities.items() if v}
            resp = requests.get(f"{API_BASE}/users/", params=params, headers=headers)
            result = resp.json()
            user_message = f"Found {len(result)} employees." if isinstance(result, list) else "No employees found."
            return {"result": result, "user_message": user_message}
        elif intent == "view_leave_types":
            resp = requests.get(f"{API_BASE}/leave-types/", headers=headers)
            result = resp.json()
            user_message = f"Found {len(result)} leave types." if isinstance(result, list) else "No leave types found."
            return {"result": result, "user_message": user_message}
        elif intent == "view_leave_statistics":
            resp = requests.get(f"{API_BASE}/leave-requests/statistics/", headers=headers)
            result = resp.json()
            user_message = "Leave statistics retrieved." if resp.status_code < 400 else result.get('detail', 'Error getting leave statistics.')
            return {"result": result, "user_message": user_message}
        elif intent == "export_leave_data":
            resp = requests.get(f"{API_BASE}/leave-requests/export/", headers=headers)
            result = resp.json()
            user_message = "Leave data exported successfully." if resp.status_code < 400 else result.get('detail', 'Error exporting leave data.')
            return {"result": result, "user_message": user_message}
    if intent == "request_leave":
        # Kiểm tra tính hợp lệ của ngày tháng trước khi gửi request
        start_date = entities["start_date"]
        end_date = entities["end_date"]
        
        is_valid, error_msg = validate_leave_dates(start_date, end_date)
        if not is_valid:
            return {"result": {}, "user_message": error_msg}
        
        data = {
            "leave_type_id": entities["leave_type_id"],
            "start_date": start_date,
            "end_date": end_date,
            "reason": entities.get("reason", "")
        }
        resp = requests.post(f"{API_BASE}/leave-requests/", json=data, headers=headers)
        result = resp.json()
        
        if resp.status_code < 400:
            user_message = f"Đơn nghỉ phép từ {data['start_date']} đến {data['end_date']} đã được gửi thành công."
        else:
            user_message = format_error_message(result, "Có lỗi xảy ra khi gửi đơn nghỉ phép. Vui lòng kiểm tra lại thông tin.")
        
        return {"result": result, "user_message": user_message}
    elif intent == "approve_leave":
        leave_id = entities["leave_request_id"]
        resp = requests.post(f"{API_BASE}/leave-requests/{leave_id}/approve/", headers=headers)
        result = resp.json()
        user_message = "Đơn nghỉ phép đã được duyệt thành công." if resp.status_code < 400 else format_error_message(result, "Có lỗi xảy ra khi duyệt đơn nghỉ phép.")
        return {"result": result, "user_message": user_message}
    elif intent == "deny_leave":
        leave_id = entities["leave_request_id"]
        resp = requests.post(f"{API_BASE}/leave-requests/{leave_id}/deny/", headers=headers)
        result = resp.json()
        user_message = "Đơn nghỉ phép đã bị từ chối." if resp.status_code < 400 else format_error_message(result, "Có lỗi xảy ra khi từ chối đơn nghỉ phép.")
        return {"result": result, "user_message": user_message}
    elif intent == "add_employee":
        if role != "hr":
            return {"result": {}, "user_message": "Chỉ HR mới có thể thêm nhân viên."}
        # Mapping department_name -> department_id nếu cần
        department_id = entities.get("department_id")
        if not department_id and "department_name" in entities:
            department_id = get_department_id_by_name(entities["department_name"], user_token)
        if not department_id:
            return {"result": {}, "user_message": "Không tìm thấy phòng ban."}
        data = {
            "full_name": entities["full_name"],
            "email": entities["email"],
            "department": department_id,
            "role": "employee"
        }
        # Có thể bổ sung các trường khác nếu backend hỗ trợ
        resp = requests.post(f"{API_BASE}/users/", json=data, headers=headers)
        result = resp.json()
        user_message = f"Nhân viên {data['full_name']} đã được thêm thành công." if resp.status_code < 400 else format_error_message(result, "Có lỗi xảy ra khi thêm nhân viên.")
        return {"result": result, "user_message": user_message}
    elif intent == "add_department":
        if role != "hr":
            return {"result": {}, "user_message": "Chỉ HR mới có thể thêm phòng ban."}
        data = {
            "name": entities["name"],
            "description": entities.get("description", "")
        }
        resp = requests.post(f"{API_BASE}/departments/", json=data, headers=headers)
        result = resp.json()
        user_message = f"Phòng ban {data['name']} đã được thêm thành công." if resp.status_code < 400 else format_error_message(result, "Có lỗi xảy ra khi thêm phòng ban.")
        return {"result": result, "user_message": user_message}
    elif intent == "assign_department_lead":
        if role != "hr":
            return {"result": {}, "user_message": "Only HR can assign department leads."}
        dept_id = entities["department_id"]
        data = {"email": entities["email"]}
        resp = requests.post(f"{API_BASE}/departments/{dept_id}/assign-lead/", json=data, headers=headers)
        result = resp.json()
        user_message = f"Department lead assigned." if resp.status_code < 400 else result.get('detail', 'Error assigning department lead.')
        return {"result": result, "user_message": user_message}
    elif intent == "update_leave_balance":
        if role != "hr":
            return {"result": {}, "user_message": "Only HR can update leave balance."}
        balance_id = entities["leave_balance_id"]
        data = {"balance": entities["balance"]}
        resp = requests.put(f"{API_BASE}/leave-balances/{balance_id}/", json=data, headers=headers)
        result = resp.json()
        user_message = f"Leave balance updated." if resp.status_code < 400 else result.get('detail', 'Error updating leave balance.')
        return {"result": result, "user_message": user_message}
    elif intent == "change_leave_decision":
        leave_id = entities["leave_request_id"]
        data = {"status": entities["status"]}
        resp = requests.post(f"{API_BASE}/leave-requests/{leave_id}/change_decision/", json=data, headers=headers)
        result = resp.json()
        user_message = f"Leave decision changed." if resp.status_code < 400 else result.get('detail', 'Error changing leave decision.')
        return {"result": result, "user_message": user_message}
    elif intent == "delete_employee":
        if role != "hr":
            return {"result": {}, "user_message": "Only HR can delete employees."}
        user_id = entities["user_id"]
        resp = requests.delete(f"{API_BASE}/users/{user_id}/", headers=headers)
        result = resp.json() if resp.content else {}
        user_message = "Employee deleted successfully." if resp.status_code < 400 else result.get('detail', 'Error deleting employee.')
        return {"result": result, "user_message": user_message}
    elif intent == "update_employee":
        if role != "hr":
            return {"result": {}, "user_message": "Only HR can update employees."}
        user_id = entities["user_id"]
        data = {k: v for k, v in entities.items() if k != "user_id" and v}
        resp = requests.put(f"{API_BASE}/users/{user_id}/", json=data, headers=headers)
        result = resp.json()
        user_message = "Employee updated successfully." if resp.status_code < 400 else result.get('detail', 'Error updating employee.')
        return {"result": result, "user_message": user_message}
    elif intent == "delete_department":
        if role != "hr":
            return {"result": {}, "user_message": "Only HR can delete departments."}
        dept_id = entities["department_id"]
        resp = requests.delete(f"{API_BASE}/departments/{dept_id}/", headers=headers)
        result = resp.json() if resp.content else {}
        user_message = "Department deleted successfully." if resp.status_code < 400 else result.get('detail', 'Error deleting department.')
        return {"result": result, "user_message": user_message}
    elif intent == "update_department":
        if role != "hr":
            return {"result": {}, "user_message": "Only HR can update departments."}
        dept_id = entities["department_id"]
        data = {k: v for k, v in entities.items() if k != "department_id" and v}
        resp = requests.put(f"{API_BASE}/departments/{dept_id}/", json=data, headers=headers)
        result = resp.json()
        user_message = "Department updated successfully." if resp.status_code < 400 else result.get('detail', 'Error updating department.')
        return {"result": result, "user_message": user_message}
    elif intent == "add_leave_type":
        if role != "hr":
            return {"result": {}, "user_message": "Only HR can add leave types."}
        data = {
            "name": entities["name"],
            "description": entities.get("description", "")
        }
        resp = requests.post(f"{API_BASE}/leave-types/", json=data, headers=headers)
        result = resp.json()
        user_message = f"Leave type {data['name']} added." if resp.status_code < 400 else result.get('detail', 'Error adding leave type.')
        return {"result": result, "user_message": user_message}
    elif intent == "update_leave_type":
        if role != "hr":
            return {"result": {}, "user_message": "Only HR can update leave types."}
        leave_type_id = entities["leave_type_id"]
        data = {k: v for k, v in entities.items() if k != "leave_type_id" and v}
        resp = requests.put(f"{API_BASE}/leave-types/{leave_type_id}/", json=data, headers=headers)
        result = resp.json()
        user_message = "Leave type updated successfully." if resp.status_code < 400 else result.get('detail', 'Error updating leave type.')
        return {"result": result, "user_message": user_message}
    elif intent == "delete_leave_type":
        if role != "hr":
            return {"result": {}, "user_message": "Only HR can delete leave types."}
        leave_type_id = entities["leave_type_id"]
        resp = requests.delete(f"{API_BASE}/leave-types/{leave_type_id}/", headers=headers)
        result = resp.json() if resp.content else {}
        user_message = "Leave type deleted successfully." if resp.status_code < 400 else result.get('detail', 'Error deleting leave type.')
        return {"result": result, "user_message": user_message}
    else:
        return {"result": {}, "user_message": "Intent not recognized or not supported."}

# Tối ưu prompt cho LLM

def get_current_year():
    """Lấy năm hiện tại để sử dụng trong prompt"""
    from datetime import datetime
    return datetime.now().year

def extract_intent_entities(message, chain=None):
    if chain:
        current_year = get_current_year()
        prompt = f"""
        You are an HR assistant. The user may ask in Vietnamese or English. Your job is to extract the user's intent and entities from the following message.
        Only use one of these valid intents (in English): request_leave, approve_leave, deny_leave, view_leave_balance, view_leave_history, pending_leave_requests, add_employee, add_department, assign_department_lead, view_profile, list_employees, list_departments, update_leave_balance, change_leave_decision, delete_employee, update_employee, delete_department, update_department, view_employee_details, search_employees, view_leave_types, add_leave_type, update_leave_type, delete_leave_type, view_leave_statistics, export_leave_data.
        Always return a valid JSON object in the format: {{"intent": <intent>, "entities": <entities>}}
        If the intent is not recognized, return: {{"intent": "unknown", "entities": {{}}}}
        
        IMPORTANT: For dates, always use the current year ({current_year}) unless explicitly specified by the user. If user only mentions day and month (e.g., "6 tháng 8"), assume current year {current_year}.
        
        Here are some examples:
        - "Tôi muốn xin nghỉ phép từ 10/7 đến 12/7 vì lý do cá nhân."
          Output: {{"intent": "request_leave", "entities": {{"leave_type_id": 1, "start_date": "{current_year}-07-10", "end_date": "{current_year}-07-12", "reason": "Lý do cá nhân"}}}}
        - "Cho tôi xem thông tin cá nhân."
          Output: {{"intent": "view_profile", "entities": {{}}}}
        - "Duyệt đơn nghỉ phép số 123."
          Output: {{"intent": "approve_leave", "entities": {{"leave_request_id": 123}}}}
        - "Tôi còn bao nhiêu ngày phép?"
          Output: {{"intent": "view_leave_balance", "entities": {{}}}}
        - "Thêm nhân viên tên Nguyễn Văn A, email a@example.com vào phòng Kế toán."
          Output: {{"intent": "add_employee", "entities": {{"full_name": "Nguyễn Văn A", "email": "a@example.com", "department_id": 2}}}}
        - "List all departments."
          Output: {{"intent": "list_departments", "entities": {{}}}}
        - "Update leave balance for John Doe to 10 days."
          Output: {{"intent": "update_leave_balance", "entities": {{"leave_balance_id": 5, "balance": 10}}}}
        - "Xóa nhân viên có ID 5."
          Output: {{"intent": "delete_employee", "entities": {{"user_id": 5}}}}
        - "Cập nhật thông tin nhân viên ID 3, email mới là new@example.com."
          Output: {{"intent": "update_employee", "entities": {{"user_id": 3, "email": "new@example.com"}}}}
        - "Xem chi tiết nhân viên ID 7."
          Output: {{"intent": "view_employee_details", "entities": {{"user_id": 7}}}}
        - "Tìm kiếm nhân viên tên Nguyễn."
          Output: {{"intent": "search_employees", "entities": {{"search_term": "Nguyễn"}}}}
        - "Xem danh sách loại nghỉ phép."
          Output: {{"intent": "view_leave_types", "entities": {{}}}}
        - "Thêm loại nghỉ phép mới tên 'Nghỉ ốm', mô tả 'Nghỉ do ốm đau'."
          Output: {{"intent": "add_leave_type", "entities": {{"name": "Nghỉ ốm", "description": "Nghỉ do ốm đau"}}}}
        Message: "{message}"
        """
        response = chain.invoke({"input": prompt})
        content = response.content.strip()
        # Loại bỏ markdown code block nếu có
        if content.startswith("```"):
            # Loại bỏ tất cả các dòng bắt đầu và kết thúc bằng ``` hoặc ```json
            content = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", content, flags=re.MULTILINE).strip()
        try:
            data = json.loads(content)
            if not isinstance(data, dict) or "intent" not in data or "entities" not in data:
                return {"intent": "unknown", "entities": {}}
            return postprocess_intent(data)
        except Exception as e:
            print("LLM response parse error:", response.content)
            return {"intent": "unknown", "entities": {}}
    # Dữ liệu mẫu cho test nhanh
    msg = message.lower()
    if "nghỉ phép" in msg or ("leave" in msg and "request" in msg):
        current_year = get_current_year()
        return postprocess_intent({
            "intent": "request_leave",
            "entities": {
                "leave_type_id": 1,
                "start_date": f"{current_year}-07-10",
                "end_date": f"{current_year}-07-12",
                "reason": "Lý do cá nhân" if "nghỉ phép" in msg else "personal reasons"
            }
        })
    if any(kw in msg for kw in ["profile", "my info", "personal info", "thông tin cá nhân", "hồ sơ"]):
        return postprocess_intent({
            "intent": "view_profile",
            "entities": {}
        })
    return {"intent": "unknown", "entities": {}} 