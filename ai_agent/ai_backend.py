from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import os
from intent_api_mapping import extract_intent_entities, call_api

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
    # 1. Phân tích intent và entity từ message
    ai_result = extract_intent_entities(msg.message, chain=chain)
    intent = ai_result.get("intent")
    entities = ai_result.get("entities", {})

    # 2. Gọi API backend thực thi intent, truyền thêm user_role
    api_result = call_api(intent, entities, user_token=msg.token, user_role=msg.role, user_message_input=msg.message)

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