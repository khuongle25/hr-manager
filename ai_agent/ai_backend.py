from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import os
from schema_registry import schema_registry
from intent_api_mapping import extract_intent_entities, call_api, get_role_from_token
from constants import DEPARTMENT_MAPPINGS, LEAVE_TYPE_MAPPINGS, ROLE_MAPPINGS, STATUS_MAPPINGS

# Lấy Gemini API key từ biến môi trường
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAy1zLhUYfX-B_r71zENYncn18vJDp0V5k")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hoặc chỉ định domain frontend, ví dụ: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=GEMINI_API_KEY
)

def get_current_year():
    """Lấy năm hiện tại để sử dụng trong prompt"""
    from datetime import datetime
    return datetime.now().year

def generate_enhanced_prompt(message: str) -> str:
    """Tạo prompt chi tiết với schema information"""
    current_year = get_current_year()
    
    # Lấy tất cả intents từ schema
    available_intents = list(schema_registry.endpoints.keys())
    
    # Tạo mapping info từ constants
    dept_info = ", ".join([f"{k}={v}" for k, v in list(DEPARTMENT_MAPPINGS.items())[:10]])
    leave_type_info = ", ".join([f"{k}={v}" for k, v in list(LEAVE_TYPE_MAPPINGS.items())[:8]])
    role_info = ", ".join([f"{k}={v}" for k, v in list(ROLE_MAPPINGS.items())[:6]])
    status_info = ", ".join([f"{k}={v}" for k, v in list(STATUS_MAPPINGS.items())[:8]])
    
    prompt = f"""
        Bạn là HR assistant AI. Nhiệm vụ: phân tích tin nhắn và trích xuất intent + entities.

        INTENTS HỢP LỆ: {', '.join(available_intents)}

        MAPPING THÔNG TIN:
        - Phòng ban: {dept_info}
        - Loại nghỉ phép: {leave_type_info}
        - Vai trò: {role_info}
        - Trạng thái: {status_info}

        RULES:
        1. Luôn trả về JSON: {{"intent": "<intent>", "entities": <entities>}}
        2. Sử dụng năm {current_year} nếu không chỉ định năm
        3. Map tiếng Việt sang English trong entities
        4. ⭐ QUAN TRỌNG: Với nghỉ phép, dùng "leave_type_id" (integer) chứ không phải "leave_type"
        5. ⭐ ID SELECTION: Khi user nhập "ID 123" hoặc "duyệt đơn ID 123" → extract leave_request_id: 123
        6. Nếu không nhận diện được, trả về: {{"intent": "unknown", "entities": {{}}}}

        VÍ DỤ:
        - "xin nghỉ ốm" → {{"intent": "request_leave", "entities": {{"leave_type_id": 2, ...}}}}
        - "duyệt đơn của Nguyễn Văn A" → {{"intent": "approve_leave", "entities": {{"employee_name": "Nguyễn Văn A"}}}}
        - "duyệt đơn ID 123" → {{"intent": "approve_leave", "entities": {{"leave_request_id": 123}}}}
        - "ID 123" → {{"intent": "approve_leave", "entities": {{"leave_request_id": 123}}}}

        Message: "{message}"

        Trả về JSON:
    """
    return prompt

# Định nghĩa prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Bạn là trợ lý AI cho hệ thống quản lý nhân sự. Hãy xác định ý định của người dùng và trích xuất thông tin cần thiết."),
    ("human", "{input}")
])

chain = prompt | llm

class Message(BaseModel):
    user_id: int
    role: str
    message: str
    token: str  # Thêm trường token để xác thực API backend

@app.post("/chat")
async def chat(msg: Message):
    # 1. Tạo enhanced prompt với constants
    enhanced_prompt = generate_enhanced_prompt(msg.message)
    
    # 2. Phân tích intent và entity
    ai_result = extract_intent_entities(msg.message, chain=chain, enhanced_prompt=enhanced_prompt)
    intent = ai_result.get("intent")
    entities = ai_result.get("entities", {})

    # ⭐ 2.5. LẤY ROLE TỪ DJANGO API THAY VÌ TIN FRONTEND
    actual_user_role = get_role_from_token(msg.token)
    
    if not actual_user_role:
        return {
            "user_message": "❌ Không thể xác thực user. Vui lòng đăng nhập lại.",
            "intent": intent,
            "entities": entities,
            "result": {}
        }
    
    print(f"🔥 DEBUG - Frontend role: {msg.role}, Actual role from API: {actual_user_role}")

    # 3. Gọi API backend thực thi intent, sử dụng ACTUAL role từ Django
    api_result = call_api(intent, entities, user_token=msg.token, user_role=actual_user_role, user_message_input=msg.message)

    # 3. Nếu user_message rỗng, sinh câu trả lời cuối cùng bằng Gemini
    user_message = api_result.get("user_message", "")
    result = api_result.get("result", {})
    if not user_message or user_message.strip() == "":
        # Nếu result là dict có 'results' là list, chỉ truyền phần results
        result_for_prompt = result
        if isinstance(result, dict) and 'results' in result and isinstance(result['results'], list):
            result_for_prompt = result['results']
        # Prompt mạnh mẽ, không ví dụ
        prompt_text = f'''
            Bạn là trợ lý nhân sự AI. Dưới đây là câu hỏi gốc của người dùng và KẾT QUẢ API TRẢ VỀ DƯỚI DẠNG JSON.
            - Hãy đọc kỹ kết quả JSON, DIỄN GIẢI lại kết quả này cho người dùng dựa trên câu hỏi gốc.
            - KHÔNG lặp lại câu hỏi, KHÔNG trả lời chung chung, chỉ trả lời dựa trên dữ liệu JSON.
            - Nếu là danh sách, hãy liệt kê tên, tổng số, tối đa 10 mục.
            - Nếu là thông tin cá nhân, hãy trình bày rõ ràng, ngắn gọn.
            - Nếu không có dữ liệu, hãy nói rõ cho người dùng biết.
            - Nếu là lỗi, hãy giải thích ngắn gọn, thân thiện.
            - Trả lời tự nhiên, dễ hiểu, đúng ngữ cảnh.
            - Nếu không thể trả lời, hãy nói rõ lý do.

            Câu hỏi gốc: {msg.message}
            Kết quả API (JSON): {result_for_prompt}
            Trả lời:
        '''
        response = chain.invoke({"input": prompt_text})
        user_message = response.content.strip()
    # 4. Trả về kết quả cho frontend
    return {
        "user_message": user_message,
        "intent": intent,
        "entities": entities,
        "result": result
    }