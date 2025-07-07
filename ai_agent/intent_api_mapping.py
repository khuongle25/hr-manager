import requests
import json
import re
import unicodedata
from schema_registry import schema_registry
from typing import Dict, List, Optional, Any, Union


API_BASE = "http://localhost:8000/api"

def get_role_from_token(token):
    """Lấy role từ token"""
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
    """Lấy department ID theo tên"""
    # Thử tìm trong constants trước
    dept_id = schema_registry.map_department_name_to_id(department_name)
    if dept_id:
        return dept_id
    
    # Nếu không có trong constants, gọi API
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
    
    if "non_field_errors" in result:
        errors = result["non_field_errors"]
        return f"Lỗi: {'; '.join(errors)}"
    
    if "detail" in result:
        return f"Lỗi: {result['detail']}"
    
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
  
        if start < today:
            return False, f"Ngày bắt đầu ({start_date}) không được trước ngày hiện tại ({today}). Vui lòng chọn ngày trong tương lai."
        
        if end < start:
            return False, f"Ngày kết thúc ({end_date}) không được trước ngày bắt đầu ({start_date})"
        
        return True, None
    except ValueError:
        return False, "Định dạng ngày không hợp lệ (phải là YYYY-MM-DD)"

def normalize_text(text):
    """Normalize text để so sánh"""
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    return text.lower()

def get_user_id_by_name(full_name, token):
    """Tìm user_id theo tên đầy đủ"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        search_url = f"{API_BASE}/users/?search={full_name}"
        print(f"🔥 DEBUG - Searching users: {search_url}")
        
        resp = requests.get(search_url, headers=headers, timeout=5)
        print(f"🔥 DEBUG - User search response: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"🔥 DEBUG - User search data: {data}")
            
            norm_full_name = normalize_text(full_name)
            print(f"🔥 DEBUG - Normalized search name: {norm_full_name}")
            
            # Xử lý format response
            if isinstance(data, dict) and "results" in data:
                users = data["results"]
            elif isinstance(data, list):
                users = data
            elif isinstance(data, dict) and "id" in data:
                users = [data]
            else:
                users = []
            
            print(f"🔥 DEBUG - Found {len(users)} users")
            
            # Tìm user có full_name khớp chính xác
            for u in users:
                user_full_name = u.get("full_name", "")
                norm_user_name = normalize_text(user_full_name)
                print(f"🔥 DEBUG - Comparing '{norm_user_name}' with '{norm_full_name}'")
                if norm_user_name == norm_full_name:
                    print(f"🔥 DEBUG - Exact match found: {u['id']}")
                    return u["id"]
            
            # Trả về user đầu tiên nếu không khớp chính xác
            if users:
                print(f"🔥 DEBUG - No exact match, returning first user: {users[0]['id']}")
                return users[0]["id"]
        else:
            print(f"🔥 DEBUG - User search failed: {resp.status_code} - {resp.text}")
                
    except Exception as e:
        print(f"🔥 DEBUG - Error getting user id by name: {e}")
    return None

def get_future_leave_requests(user_id, token, start_date=None, end_date=None):
    """Tìm các đơn nghỉ phép trong tương lai (start_date > today) - bao gồm cả pending và approved"""
    from datetime import date
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        params = {}  # Không filter theo status nữa
        
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        leave_url = f"{API_BASE}/leave-requests/"
        print(f"🔥 DEBUG - Getting future leave requests: {leave_url}")
        print(f"🔥 DEBUG - Params: {params}")
        
        resp = requests.get(leave_url, params=params, headers=headers, timeout=10)
        print(f"🔥 DEBUG - Leave requests response: {resp.status_code}")
        
        if resp.status_code == 403:
            print("❌ Permission denied - user cannot view leave requests")
            return []
        
        if resp.status_code != 200:
            print(f"❌ API Error: {resp.status_code} - {resp.text}")
            return []
        
        data = resp.json()
        print(f"🔥 DEBUG - Leave requests data type: {type(data)}")
        
        # Xử lý format response
        if isinstance(data, dict) and "results" in data:
            all_requests = data["results"]
        elif isinstance(data, list):
            all_requests = data
        else:
            all_requests = []
        
        print(f"🔥 DEBUG - Found {len(all_requests)} total requests")
        
        # Filter theo user_id nếu có
        if user_id:
            filtered_requests = []
            for req in all_requests:
                employee = req.get("employee", {})
                employee_id = employee.get("id") if isinstance(employee, dict) else None
                
                if employee_id == user_id:
                    filtered_requests.append(req)
            
            all_requests = filtered_requests
            print(f"🔥 DEBUG - After filtering by user_id {user_id}: {len(all_requests)} requests")
        
        # ⭐ FILTER CHỈ LẤY ĐỪN TRONG TƯƠNG LAI (start_date > today)
        today = date.today()
        future_requests = []
        
        for req in all_requests:
            try:
                start_date_str = req.get("start_date")
                if start_date_str:
                    from datetime import datetime
                    req_start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                    
                    # Chỉ lấy đơn có start_date > today
                    if req_start_date > today:
                        future_requests.append(req)
                        print(f"🔥 DEBUG - Including future request: ID {req.get('id')}, start: {start_date_str}, status: {req.get('status')}")
                    else:
                        print(f"🔥 DEBUG - Skipping past request: ID {req.get('id')}, start: {start_date_str}")
            except (ValueError, TypeError) as e:
                print(f"🔥 DEBUG - Error parsing date for request {req.get('id')}: {e}")
                continue
        
        # ⭐ SẮP XẾP ƯU TIÊN: pending trước, sau đó approved, cuối cùng denied
        def sort_priority(req):
            status = req.get("status", "").lower()
            if status == "pending":
                return 0  # Ưu tiên cao nhất
            elif status == "approved":
                return 1  # Ưu tiên thứ hai
            else:  # denied hoặc khác
                return 2  # Ưu tiên thấp nhất
        
        future_requests.sort(key=sort_priority)
        
        print(f"🔥 DEBUG - Final future requests: {len(future_requests)}")
        return future_requests
        
    except Exception as e:
        print(f"🔥 DEBUG - Error getting future leave requests: {e}")
        return []

def smart_approve_deny_logic(intent, entities, user_token, user_role):
    """Logic thông minh cho approve/deny leave với interactive selection"""
    if intent not in ["approve_leave", "deny_leave"]:
        return None
    
    print(f"🔥 DEBUG - Smart logic called for {intent}")
    print(f"🔥 DEBUG - Entities: {entities}")
    
    if "leave_request_id" in entities and entities["leave_request_id"]:
        print(f"🔥 DEBUG - Already have leave_request_id: {entities['leave_request_id']}")
        return None  # Đã có ID, không cần logic thông minh
    
    # Lấy tên nhân viên từ entities
    employee_name = entities.get("full_name") or entities.get("employee_name")
    start_date = entities.get("start_date")
    end_date = entities.get("end_date")
    
    print(f"🔥 DEBUG - Employee name: {employee_name}")
    
    if employee_name:
        # 1. Tìm user_id từ tên
        print(f"🔥 DEBUG - Looking up user_id for: {employee_name}")
        user_id = get_user_id_by_name(employee_name, user_token)
        print(f"🔥 DEBUG - Found user_id: {user_id}")
        
        if not user_id:
            return {
                "result": {}, 
                "user_message": f"❌ Không tìm thấy nhân viên tên '{employee_name}'"
            }
        
        # 2. Lấy tất cả đơn chờ duyệt của nhân viên đó
        print(f"🔥 DEBUG - Getting future requests for user_id: {user_id}")
        pending_requests = get_future_leave_requests(user_id, user_token, start_date, end_date)
        print(f"🔥 DEBUG - Found {len(pending_requests)} future requests")
        
        if not pending_requests:
            return {
                "result": {}, 
                "user_message": f"❌ Không có đơn nghỉ phép nào trong tương lai của {employee_name}"
            }
        
        if len(pending_requests) == 1:
            # Chỉ có 1 đơn → Auto approve
            print(f"🔥 DEBUG - Auto-selecting single request ID: {pending_requests[0]['id']}")
            entities["leave_request_id"] = pending_requests[0]["id"]
            return None  # Tiếp tục xử lý với ID đã có
        
        else:
            # Có nhiều đơn → Show interactive list
            print(f"🔥 DEBUG - Showing interactive list for {len(pending_requests)} requests")
            return format_interactive_leave_selection(pending_requests, employee_name, intent)
    
    elif start_date or end_date:
        # Case: "Duyệt đơn từ 15/01 đến 17/01"
        pending_requests = get_future_leave_requests(None, user_token, start_date, end_date)
        
        if not pending_requests:
            date_range = f"từ {start_date}" if start_date else f"đến {end_date}"
            if start_date and end_date:
                date_range = f"từ {start_date} đến {end_date}"
            return {
                "result": {}, 
                "user_message": f"❌ Không có đơn nghỉ phép nào trong tương lai {date_range}"
            }
        
        if len(pending_requests) == 1:
            entities["leave_request_id"] = pending_requests[0]["id"]
            return None
        else:
            return format_interactive_leave_selection(pending_requests, None, intent, start_date, end_date)
    
    else:
        # Case: "Duyệt đơn nghỉ phép" (không có thông tin gì)
        all_pending = get_future_leave_requests(None, user_token)
        
        if not all_pending:
            return {
                "result": {}, 
                "user_message": "❌ Không có đơn nghỉ phép nào trong tương lai"
            }
        
        # Show tất cả đơn trong tương lai (limit 10)
        return format_interactive_leave_selection(all_pending[:10], None, intent)

def format_interactive_leave_selection(requests, employee_name, intent, start_date=None, end_date=None):
    """Format danh sách đơn nghỉ phép để user chọn - giao diện đơn giản dễ đọc"""
    action = "duyệt" if intent == "approve_leave" else "từ chối"
    
    # ⭐ THỐNG KÊ ĐƠN GIẢN
    pending_count = sum(1 for req in requests if req.get('status', '').lower() == 'pending')
    approved_count = sum(1 for req in requests if req.get('status', '').lower() == 'approved')
    denied_count = sum(1 for req in requests if req.get('status', '').lower() == 'denied')
    
    # Header đơn giản
    if employee_name:
        header = f"📋 Đơn nghỉ phép trong tương lai của {employee_name}:\n"
    elif start_date or end_date:
        date_info = f"từ {start_date}" if start_date else f"đến {end_date}"
        if start_date and end_date:
            date_info = f"từ {start_date} đến {end_date}"
        header = f"📋 Đơn nghỉ phép trong tương lai {date_info}:\n"
    else:
        header = f"📋 Đơn nghỉ phép trong tương lai:\n"
    
    # Thống kê ngắn gọn
    stats = f"Tổng: {len(requests)} đơn"
    if pending_count > 0:
        stats += f" | Chờ duyệt: {pending_count}"
    if approved_count > 0:
        stats += f" | Đã duyệt: {approved_count}"
    if denied_count > 0:
        stats += f" | Đã từ chối: {denied_count}"
    
    # ⭐ FORMAT TỪNG ĐƠN ĐƠN GIẢN
    leave_list = []
    for i, req in enumerate(requests, 1):
        employee_info = req.get('employee', {})
        employee_name_display = employee_info.get('full_name', 'Unknown') if isinstance(employee_info, dict) else 'Unknown'
        
        leave_type_info = req.get('leave_type', {})
        leave_type_name = leave_type_info.get('name', 'Unknown') if isinstance(leave_type_info, dict) else 'Unknown'
        
        # ⭐ STATUS ĐƠN GIẢN - CHỈ DÙNG EMOJI
        status = req.get('status', '').lower()
        if status == 'pending':
            status_emoji = "⏳"
        elif status == 'approved':
            status_emoji = "✅"
        elif status == 'denied':
            status_emoji = "❌"
        else:
            status_emoji = "❓"
        
        # ⭐ FORMAT ĐƠN GIẢN - 1 DÒNG
        leave_item = (
            f"{i}. ID {req['id']} - {employee_name_display} | "
            f"{status_emoji} {status.title()} | "
            f"{leave_type_name} | "
            f"{req['start_date']} → {req['end_date']} | "
            f"Lý do: {req.get('reason', 'Không có')[:30]}{'...' if len(req.get('reason', '')) > 30 else ''}"
        )
        leave_list.append(leave_item)
    
    # Footer đơn giản
    footer = (
        f"\n💡 Để {action} đơn cụ thể:\n"
        f"• Nhập: \"{action.capitalize()} đơn ID [số]\" (VD: \"{action.capitalize()} đơn ID 123\")\n"
        f"• Hoặc chỉ nhập: \"ID [số]\" (VD: \"ID 123\")"
    )
    
    full_message = header + stats + "\n\n" + "\n".join(leave_list) + footer
    
    return {
        "result": {
            "future_requests": requests,
            "action_type": intent,
            "count": len(requests),
            "stats": {
                "pending": pending_count,
                "approved": approved_count, 
                "denied": denied_count
            }
        }, 
        "user_message": full_message
    }

def call_api(intent, entities, user_token, user_role=None, user_message_input=None):
    """Main API call function với proper permission checking"""
    # 1. Map Vietnamese fields to English sử dụng schema registry
    entities = schema_registry.map_vietnamese_fields(entities)
    
    # 2. Map các field đặc biệt
    if 'employee_name' in entities and 'full_name' not in entities:
        entities['full_name'] = entities['employee_name']
    
    if 'decision' in entities and 'status' not in entities:
        entities['status'] = entities['decision']
        
    # 3. Map leave_type to leave_type_id
    if 'leave_type' in entities and 'leave_type_id' not in entities:
        leave_type_name = entities['leave_type']
        leave_type_id = schema_registry.map_leave_type_name_to_id(leave_type_name)
        if leave_type_id:
            entities['leave_type_id'] = leave_type_id
            del entities['leave_type']  # Remove old key
        else:
            return {
                "result": {}, 
                "user_message": f"Không tìm thấy loại nghỉ phép: {leave_type_name}"
            }
    
    # 4. Map status values
    if 'status' in entities and entities['status']:
        status_val = str(entities['status']).strip().lower()
        mapped_status = schema_registry.map_status_vietnamese_to_english(status_val)
        entities['status'] = mapped_status
    
    # 5. Map department names to IDs if needed
    if 'department_name' in entities and 'department_id' not in entities:
        dept_id = schema_registry.map_department_name_to_id(entities['department_name'])
        if dept_id:
            entities['department_id'] = dept_id
    
    # 6. Map leave type names to IDs if needed
    if 'leave_type_name' in entities and 'leave_type_id' not in entities:
        leave_type_id = schema_registry.map_leave_type_name_to_id(entities['leave_type_name'])
        if leave_type_id:
            entities['leave_type_id'] = leave_type_id

    # 7. Check VIEW-LEVEL permissions sử dụng schema registry
    if not schema_registry.check_role_permission(intent, user_role):
        permission_rule = schema_registry.get_permission_rule(intent)
        allowed_roles = permission_rule.allowed_roles if permission_rule else ["unknown"]
        return {
            "result": {}, 
            "user_message": f"❌ Bạn không có quyền thực hiện chức năng này. Cần quyền: {', '.join(allowed_roles)}"
        }
            
    # ⭐ 8. SMART LOGIC TRƯỚC VALIDATION (di chuyển lên đây)
    headers = {"Authorization": f"Bearer {user_token}"}
    smart_result = smart_approve_deny_logic(intent, entities, user_token, user_role)
    if smart_result:
        return smart_result
    
    # 9. Check OBJECT-LEVEL permissions nếu cần
    if schema_registry.requires_object_level_check(intent):
        object_permission_result = check_object_level_permission(intent, entities, user_token, user_role)
        if object_permission_result:
            return object_permission_result   
    
    # 9. Validate entities sử dụng schema registry (AFTER smart logic)
    is_valid, validation_errors = schema_registry.validate_entities(intent, entities)
    if not is_valid:
        return {"result": {}, "user_message": "Dữ liệu không hợp lệ: " + "; ".join(validation_errors)}
    
    # 10. Check missing required fields (AFTER smart logic)
    missing_fields = schema_registry.get_required_fields(intent)
    missing = [field for field in missing_fields if field not in entities or not entities[field]]
    
    if missing:
        field_descriptions = [schema_registry.get_field_description(intent, field) for field in missing]
        return {
            "result": {},
            "user_message": f"Bạn cần cung cấp thêm thông tin: {', '.join(field_descriptions)} để thực hiện chức năng này.",
        }
    
    # 11. Execute API calls based on intent
    return execute_api_call(intent, entities, headers, user_message_input)


def check_object_level_permission(intent: str, entities: Dict[str, Any], user_token: str, user_role: str) -> Optional[Dict]:
    """Kiểm tra object-level permissions"""
    permission_rule = schema_registry.get_permission_rule(intent)
    if not permission_rule or not permission_rule.object_level_check:
        return None
    
    check_type = permission_rule.object_level_check
    
    print(f"🔥 DEBUG - Object level permission check for intent: {intent}")
    print(f"🔥 DEBUG - User role: {user_role}")
    print(f"🔥 DEBUG - Check type: {check_type}")
    print(f"🔥 DEBUG - Entities: {entities}")
    
    # Lấy thông tin user hiện tại
    current_user_info = get_current_user_info(user_token)
    print(f"🔥 DEBUG - Current user info: {current_user_info}")
    
    if not current_user_info:
        return {"result": {}, "user_message": "❌ Không thể xác thực user"}
    
    current_user_id = current_user_info.get("id")
    print(f"🔥 DEBUG - Current user ID: {current_user_id}")
    
    if check_type == "team_member_or_hr":
        # For approve/deny leave - check if leave belongs to team member
        if user_role == "hr":
            print("🔥 DEBUG - HR role, allowing all permissions")
            return None  # HR có quyền với tất cả
        
        if user_role == "team_lead":
            print("🔥 DEBUG - Team lead role, checking team membership")
            
            # ⭐ NGĂN TEAM LEAD TỰ DUYỆT ĐƠN CỦA MÌNH
            leave_request_id = entities.get("leave_request_id")
            if leave_request_id:
                # Lấy thông tin leave request để check employee
                try:
                    headers = {"Authorization": f"Bearer {user_token}"}
                    resp = requests.get(f"{API_BASE}/leave-requests/{leave_request_id}/", headers=headers, timeout=5)
                    if resp.status_code == 200:
                        leave_data = resp.json()
                        employee = leave_data.get("employee", {})
                        employee_id = employee.get("id") if isinstance(employee, dict) else None
                        
                        if employee_id == current_user_id:
                            return {"result": {}, "user_message": "❌ Bạn không thể tự duyệt/từ chối đơn nghỉ phép của chính mình. Vui lòng liên hệ HR hoặc cấp trên."}
                except Exception as e:
                    print(f"🔥 DEBUG - Error checking self-approval: {e}")
            
            # Cần kiểm tra leave request có thuộc team member không
            employee_name = entities.get("full_name") or entities.get("employee_name")
            
            print(f"🔥 DEBUG - Leave request ID: {leave_request_id}")
            print(f"🔥 DEBUG - Employee name: {employee_name}")
            
            if leave_request_id:
                # Kiểm tra leave request cụ thể
                print(f"🔥 DEBUG - Checking leave request {leave_request_id} with team lead {current_user_id}")
                is_member, debug_info = is_leave_request_from_team_member_with_debug(leave_request_id, current_user_id, user_token)
                if not is_member:
                    print("🔥 DEBUG - Permission denied: not team member")
                    return {"result": {}, "user_message": f"❌ Bạn chỉ có thể duyệt/từ chối đơn của nhân viên trong team\n\nDebug info: {debug_info}"}
                else:
                    print("🔥 DEBUG - Permission granted: is team member")
            
            elif employee_name:
                # Kiểm tra nhân viên có thuộc team không
                employee_id = get_user_id_by_name(employee_name, user_token)
                print(f"🔥 DEBUG - Employee ID from name: {employee_id}")
                if employee_id:
                    is_member, debug_info = is_team_member_with_debug(employee_id, current_user_id, user_token)
                    if not is_member:
                        return {"result": {}, "user_message": f"❌ {employee_name} không thuộc team của bạn\n\nDebug info: {debug_info}"}
        
        return None  # Permission OK
    
    elif check_type == "own_or_team_or_hr":
        # For viewing data - employee sees own, team_lead sees team, hr sees all
        if user_role == "hr":
            return None  # HR có quyền với tất cả
        
        target_user_id = entities.get("user_id") or entities.get("employee_id")
        if not target_user_id:
            return None  # Không có target user - OK (sẽ filter ở backend)
        
        if user_role == "employee" and target_user_id != current_user_id:
            return {"result": {}, "user_message": "❌ Bạn chỉ có thể xem thông tin của mình"}
        
        if user_role == "team_lead":
            is_member, debug_info = is_team_member_with_debug(target_user_id, current_user_id, user_token)
            if not is_member:
                return {"result": {}, "user_message": f"❌ Bạn chỉ có thể xem thông tin của nhân viên trong team\n\nDebug info: {debug_info}"}
        
        return None  # Permission OK
    
    elif check_type == "team_or_hr":
        # For listing/searching - team_lead sees team, hr sees all
        if user_role == "hr":
            return None  # HR có quyền với tất cả
        
        if user_role == "team_lead":
            return None  # Team Lead OK, backend sẽ filter
        
        return {"result": {}, "user_message": "❌ Chỉ Team Lead và HR mới có quyền này"}
    
    return None  # Default OK

def get_current_user_info(token: str) -> Optional[Dict]:
    """Lấy thông tin user hiện tại từ token"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{API_BASE}/me/", headers=headers, timeout=5)
        print(f"🔥 DEBUG - Get current user API response: {resp.status_code}")
        
        if resp.status_code == 200:
            user_info = resp.json()
            print(f"🔥 DEBUG - Current user API data: {user_info}")
            return user_info
        else:
            print(f"🔥 DEBUG - Failed to get current user: {resp.text}")
    except Exception as e:
        print(f"🔥 DEBUG - Error getting current user info: {e}")
    return None

def is_leave_request_from_team_member_with_debug(leave_request_id: int, team_lead_id: int, token: str) -> tuple[bool, str]:
    """Kiểm tra leave request có thuộc team member của team lead không - với debug info"""
    print(f"🔥 DEBUG - Starting leave request team check: leave_id={leave_request_id}, team_lead_id={team_lead_id}")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{API_BASE}/leave-requests/{leave_request_id}/", headers=headers, timeout=5)
        
        debug_info = f"Leave request {leave_request_id} API: {resp.status_code}"
        print(f"🔥 DEBUG - Leave request API response: {resp.status_code}")
        
        if resp.status_code == 200:
            leave_data = resp.json()
            print(f"🔥 DEBUG - Leave request data: {leave_data}")
            
            employee = leave_data.get("employee", {})
            employee_id = employee.get("id") if isinstance(employee, dict) else None
            
            debug_info += f" | Employee ID: {employee_id}"
            print(f"🔥 DEBUG - Employee ID from leave request: {employee_id}")
            
            if employee_id:
                print(f"🔥 DEBUG - Checking team membership for employee {employee_id} vs lead {team_lead_id}")
                is_member, member_debug = is_team_member_with_debug(employee_id, team_lead_id, token)
                debug_info += f" | {member_debug}"
                print(f"🔥 DEBUG - Team membership result: {is_member}")
                print(f"🔥 DEBUG - Full debug info: {debug_info}")
                return is_member, debug_info
            else:
                print("🔥 DEBUG - No employee ID found in leave request")
                return False, debug_info + " | No employee ID found"
        else:
            print(f"🔥 DEBUG - Leave request API failed: {resp.text}")
            return False, debug_info + f" | Error: {resp.text[:100]}"
    except Exception as e:
        print(f"🔥 DEBUG - Exception in leave request team check: {e}")
        return False, f"Exception: {str(e)}"

def is_team_member_with_debug(employee_id: int, team_lead_id: int, token: str) -> tuple[bool, str]:
    """Kiểm tra employee có thuộc team của team lead không - với debug info"""
    print(f"🔥 DEBUG - Starting team membership check: employee_id={employee_id}, team_lead_id={team_lead_id}")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        debug_info = f"Checking employee {employee_id} vs lead {team_lead_id}"
        
        # Query departments để tìm team lead departments
        dept_resp = requests.get(f"{API_BASE}/departments/", headers=headers, timeout=5)
        debug_info += f" | Dept API: {dept_resp.status_code}"
        print(f"🔥 DEBUG - Departments API response: {dept_resp.status_code}")
        
        if dept_resp.status_code != 200:
            print(f"🔥 DEBUG - Departments API failed: {dept_resp.text}")
            return False, debug_info + f" | Dept error: {dept_resp.text[:50]}"
        
        departments_data = dept_resp.json()
        print(f"🔥 DEBUG - Departments data type: {type(departments_data)}")
        
        # Handle paginated response
        if isinstance(departments_data, dict) and "results" in departments_data:
            departments = departments_data["results"]
        elif isinstance(departments_data, list):
            departments = departments_data
        else:
            departments = []
        
        debug_info += f" | Found {len(departments)} depts"
        print(f"🔥 DEBUG - Found {len(departments)} departments")
        
        # Tìm departments mà team_lead là leader
        team_lead_department_ids = []
        for dept in departments:
            leads = dept.get("lead", [])
            print(f"🔥 DEBUG - Department {dept.get('name')} (ID: {dept.get('id')}) leads: {leads}")
            
            # Check if team_lead_id is in the leads
            for lead in leads:
                if isinstance(lead, dict):
                    lead_id = lead.get("id")
                elif isinstance(lead, int):
                    lead_id = lead
                else:
                    continue
                    
                print(f"🔥 DEBUG - Checking lead {lead_id} == {team_lead_id}: {lead_id == team_lead_id}")
                    
                if lead_id == team_lead_id:
                    team_lead_department_ids.append(dept.get("id"))
                    debug_info += f" | Lead of dept {dept.get('id')} ({dept.get('name')})"
                    print(f"🔥 DEBUG - Team lead {team_lead_id} is leader of department {dept.get('id')} ({dept.get('name')})")
        
        debug_info += f" | Lead departments: {team_lead_department_ids}"
        print(f"🔥 DEBUG - Team lead departments: {team_lead_department_ids}")
        
        if not team_lead_department_ids:
            print("🔥 DEBUG - Team lead has no departments")
            return False, debug_info + " | Team lead has no departments"
        
        # Lấy thông tin employee department
        emp_resp = requests.get(f"{API_BASE}/users/{employee_id}/", headers=headers, timeout=5)
        debug_info += f" | Emp API: {emp_resp.status_code}"
        print(f"🔥 DEBUG - Employee API response: {emp_resp.status_code}")
        
        if emp_resp.status_code != 200:
            print(f"🔥 DEBUG - Employee API failed: {emp_resp.text}")
            return False, debug_info + f" | Emp error: {emp_resp.text[:50]}"
        
        employee_data = emp_resp.json()
        print(f"🔥 DEBUG - Employee data: {employee_data}")
        
        # Employee chỉ có 1 department field
        employee_dept = employee_data.get("department")
        employee_dept_id = None
        
        if isinstance(employee_dept, dict):
            employee_dept_id = employee_dept.get("id")
        elif isinstance(employee_dept, int):
            employee_dept_id = employee_dept
        
        debug_info += f" | Emp dept: {employee_dept_id}"
        print(f"🔥 DEBUG - Employee department ID: {employee_dept_id}")
        
        # Kiểm tra employee department có trong team lead departments không
        is_team_member = employee_dept_id in team_lead_department_ids
        
        debug_info += f" | Is member: {is_team_member}"
        print(f"🔥 DEBUG - Is team member: {is_team_member}")
        print(f"🔥 DEBUG - Final result: employee dept {employee_dept_id} in {team_lead_department_ids} = {is_team_member}")
        
        return is_team_member, debug_info
        
    except Exception as e:
        print(f"🔥 DEBUG - Exception in team membership check: {e}")
        return False, f"Exception in team check: {str(e)}"

def execute_api_call(intent, entities, headers, user_message_input=None):
    """Execute actual API calls"""
    
    # Read-only operations (trả về dữ liệu)
    READ_OPERATIONS = {
        "view_profile": {
            "url": f"{API_BASE}/me/",
            "method": "GET",
            "message_generator": lambda r: f"Name: {r.get('full_name', '')}, Email: {r.get('email', '')}, Role: {r.get('role', '')}."
        },
        "list_employees": {
            "url": f"{API_BASE}/users/",
            "method": "GET",
            "params": lambda e: {"department": e.get("department_id")} if "department_id" in e else {},
            "message_generator": lambda r: ""  # Let AI generate message
        },
        "list_departments": {
            "url": f"{API_BASE}/departments/",
            "method": "GET",
            "message_generator": lambda r: f"There are {len(r)} departments." if isinstance(r, list) else "No departments found."
        },
        "view_leave_balance": {
            "url": f"{API_BASE}/leave-balances/",
            "method": "GET",
            "message_generator": lambda r: f"Bạn còn {r[0].get('balance', 0)} ngày nghỉ phép." if isinstance(r, list) and r else "Không tìm thấy thông tin ngày nghỉ phép."
        },
        "view_leave_history": {
            "url": f"{API_BASE}/leave-requests/",
            "method": "GET",
            "message_generator": lambda r: f"Bạn có {len(r)} đơn nghỉ phép." if isinstance(r, list) else "Không tìm thấy lịch sử nghỉ phép."
        },
        "pending_leave_requests": {
            "url": f"{API_BASE}/leave-requests/",
            "method": "GET",
            "params": lambda e: {"status": "pending"},
            "message_generator": lambda r: f"Có {len(r)} đơn nghỉ phép đang chờ duyệt." if isinstance(r, list) else "Không có đơn nghỉ phép nào đang chờ duyệt."
        },
        "view_employee_details": {
            "url": lambda e: f"{API_BASE}/users/{e['user_id']}/",
            "method": "GET",
            "message_generator": lambda r: f"Employee: {r.get('full_name', '')}, Email: {r.get('email', '')}, Department: {r.get('department', '')}"
        },
        "search_employees": {
            "url": f"{API_BASE}/users/",
            "method": "GET",
            "params": lambda e: {k: v for k, v in e.items() if v},
            "message_generator": lambda r: f"Found {len(r)} employees." if isinstance(r, list) else "No employees found."
        },
        "view_leave_types": {
            "url": f"{API_BASE}/leave-types/",
            "method": "GET",
            "message_generator": lambda r: f"Found {len(r)} leave types." if isinstance(r, list) else "No leave types found."
        },
    }
    
    # Handle read operations
    if intent in READ_OPERATIONS:
        operation = READ_OPERATIONS[intent]
        url = operation["url"](entities) if callable(operation["url"]) else operation["url"]
        params = operation.get("params", lambda e: {})(entities)
        
        resp = requests.get(url, params=params, headers=headers)
        result = resp.json() if resp.content else {}
        
        if resp.status_code < 400:
            user_message = operation["message_generator"](result)
        else:
            user_message = result.get('detail', 'Error occurred.')
        
        return {"result": result, "user_message": user_message}
    
    # Handle write operations
    return execute_write_operation(intent, entities, headers)

def execute_write_operation(intent, entities, headers):
    """Execute write operations (POST, PUT, DELETE)"""
    
    if intent == "request_leave":
        # Validate dates
        is_valid, error_msg = validate_leave_dates(entities["start_date"], entities["end_date"])
        if not is_valid:
            return {"result": {}, "user_message": error_msg}
        
        data = {
            "leave_type_id": entities["leave_type_id"],  # ⭐ Đã được map ở trên
            "start_date": entities["start_date"],
            "end_date": entities["end_date"],
            "reason": entities.get("reason", "")
        }
        
        print(f"🔥 DEBUG - Sending POST to {API_BASE}/leave-requests/")  # Debug log
        print(f"🔥 DEBUG - Data: {data}")  # Debug log
        
        resp = requests.post(f"{API_BASE}/leave-requests/", json=data, headers=headers)
        result = resp.json() if resp.content else {}
        
        user_message = (f"Đơn nghỉ phép từ {data['start_date']} đến {data['end_date']} đã được gửi thành công." 
                       if resp.status_code < 400 
                       else format_error_message(result, "Có lỗi xảy ra khi gửi đơn nghỉ phép."))
        
        return {"result": result, "user_message": user_message}
    
    if intent == "add_employee":
        data = {
            "username": entities["username"],           # ✅ Correct field
            "email": entities["email"],
            "first_name": entities["first_name"],       # ✅ Correct field
            "last_name": entities["last_name"],         # ✅ Correct field  
            "password": entities["password"],
            "role": entities.get("role", "employee"),
            "department_id": entities.get("department_id"),  # ✅ Correct field
            "employee_id": entities.get("employee_id"),
            "phone": entities.get("phone"),
            "address": entities.get("address"),
            "date_of_birth": entities.get("date_of_birth"),
            "hire_date": entities.get("hire_date"),
        }
        resp = requests.post(f"{API_BASE}/users/", json=data, headers=headers)
        result = resp.json()
        
        user_message = (f"Đơn nghỉ phép từ {data['start_date']} đến {data['end_date']} đã được gửi thành công." 
                       if resp.status_code < 400 
                       else format_error_message(result, "Có lỗi xảy ra khi gửi đơn nghỉ phép."))
        
        return {"result": result, "user_message": user_message}
    
    elif intent == "approve_leave":
        leave_id = entities["leave_request_id"]
        resp = requests.post(f"{API_BASE}/leave-requests/{leave_id}/approve/", headers=headers)
        result = resp.json()
        user_message = ("Đơn nghỉ phép đã được duyệt thành công." 
                       if resp.status_code < 400 
                       else format_error_message(result, "Có lỗi xảy ra khi duyệt đơn nghỉ phép."))
        return {"result": result, "user_message": user_message}
    
    elif intent == "deny_leave":
        leave_id = entities["leave_request_id"]
        resp = requests.post(f"{API_BASE}/leave-requests/{leave_id}/deny/", headers=headers)
        result = resp.json()
        user_message = ("Đơn nghỉ phép đã bị từ chối." 
                       if resp.status_code < 400 
                       else format_error_message(result, "Có lỗi xảy ra khi từ chối đơn nghỉ phép."))
        return {"result": result, "user_message": user_message}
    
    elif intent == "add_department":
        data = {
            "name": entities["name"],
            "description": entities.get("description", "")
        }
        resp = requests.post(f"{API_BASE}/departments/", json=data, headers=headers)
        result = resp.json()
        user_message = (f"Phòng ban {data['name']} đã được thêm thành công." 
                       if resp.status_code < 400 
                       else format_error_message(result, "Có lỗi xảy ra khi thêm phòng ban."))
        return {"result": result, "user_message": user_message}
    elif intent == "assign_department_lead":
        dept_id = entities["department_id"]
        data = {"email": entities["email"]}
        resp = requests.post(f"{API_BASE}/departments/{dept_id}/assign-lead/", json=data, headers=headers)
        result = resp.json()
        user_message = f"Department lead assigned." if resp.status_code < 400 else result.get('detail', 'Error assigning department lead.')
        return {"result": result, "user_message": user_message}
    elif intent == "update_leave_balance":
        balance_id = entities["id"]  
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
        user_message = f"Đã thay đổi quyết định thành '{entities['status']}'." if resp.status_code < 400 else format_error_message(result, "Có lỗi xảy ra khi thay đổi quyết định.")
        return {"result": result, "user_message": user_message}
    elif intent == "delete_employee":
        user_id = entities["user_id"]
        resp = requests.delete(f"{API_BASE}/users/{user_id}/", headers=headers)
        result = resp.json() if resp.content else {}
        user_message = "Employee deleted successfully." if resp.status_code < 400 else result.get('detail', 'Error deleting employee.')
        return {"result": result, "user_message": user_message}
    elif intent == "update_employee":
        user_id = entities["user_id"]
        data = {k: v for k, v in entities.items() if k != "user_id" and v}
        resp = requests.put(f"{API_BASE}/users/{user_id}/", json=data, headers=headers)
        result = resp.json()
        user_message = "Employee updated successfully." if resp.status_code < 400 else result.get('detail', 'Error updating employee.')
        return {"result": result, "user_message": user_message}
    elif intent == "delete_department":
        dept_id = entities["department_id"]
        resp = requests.delete(f"{API_BASE}/departments/{dept_id}/", headers=headers)
        result = resp.json() if resp.content else {}
        user_message = "Department deleted successfully." if resp.status_code < 400 else result.get('detail', 'Error deleting department.')
        return {"result": result, "user_message": user_message}
    elif intent == "update_department":
        dept_id = entities["department_id"]
        data = {k: v for k, v in entities.items() if k != "department_id" and v}
        resp = requests.put(f"{API_BASE}/departments/{dept_id}/", json=data, headers=headers)
        result = resp.json()
        user_message = "Department updated successfully." if resp.status_code < 400 else result.get('detail', 'Error updating department.')
        return {"result": result, "user_message": user_message}
    elif intent == "add_leave_type":
        data = {
            "name": entities["name"],
            "description": entities.get("description", "")
        }
        resp = requests.post(f"{API_BASE}/leave-types/", json=data, headers=headers)
        result = resp.json()
        user_message = f"Leave type {data['name']} added." if resp.status_code < 400 else result.get('detail', 'Error adding leave type.')
        return {"result": result, "user_message": user_message}
    elif intent == "update_leave_type":
        leave_type_id = entities["leave_type_id"]
        data = {k: v for k, v in entities.items() if k != "leave_type_id" and v}
        resp = requests.put(f"{API_BASE}/leave-types/{leave_type_id}/", json=data, headers=headers)
        result = resp.json()
        user_message = "Leave type updated successfully." if resp.status_code < 400 else result.get('detail', 'Error updating leave type.')
        return {"result": result, "user_message": user_message}
    elif intent == "delete_leave_type":
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


def extract_intent_entities(message, chain=None, enhanced_prompt=None):
    """Extract intent and entities using LLM"""
    if chain:
        if enhanced_prompt:
            prompt = enhanced_prompt
        else:
            current_year = get_current_year()
            # Get available intents from schema registry
            available_intents = list(schema_registry.endpoints.keys())
            
            prompt = f"""
            You are an HR assistant. Extract intent and entities from: "{message}"
            
            Valid intents: {', '.join(available_intents)}
            Current year: {current_year}
            
            Return JSON: {{"intent": "<intent>", "entities": <entities>}}
            If unclear, return: {{"intent": "unknown", "entities": {{}}}}
            """
        
        response = chain.invoke({"input": prompt})
        content = response.content.strip()
        
        # Remove markdown code blocks
        if content.startswith("```"):
            content = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", content, flags=re.MULTILINE).strip()
        
        try:
            data = json.loads(content)
            if not isinstance(data, dict) or "intent" not in data or "entities" not in data:
                return {"intent": "unknown", "entities": {}}
            return data
        except Exception as e:
            print("LLM response parse error:", response.content)
            return {"intent": "unknown", "entities": {}}
    
    # Fallback for testing
    return {"intent": "unknown", "entities": {}}