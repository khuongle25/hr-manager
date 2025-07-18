# 🏢 Hệ thống Quản lý Nhân sự với AI Agent

## 📋 Tổng quan

Hệ thống quản lý nhân sự toàn diện được phát triển bằng **Django REST Framework**, **React**, và **AI Agent** sử dụng **LangGraph**. Hệ thống hỗ trợ 3 vai trò chính: **HR Manager**, **Team Lead**, và **Employee** với đầy đủ tính năng quản lý nghỉ phép, phòng ban và chatbot AI thông minh.

## ⭐ Tính năng chính

### 🔐 Hệ thống phân quyền 3 cấp

- **HR Manager**: Toàn quyền quản lý toàn công ty
- **Team Lead**: Quản lý nhân viên trong team, duyệt đơn nghỉ phép
- **Employee**: Xem thông tin cá nhân, gửi đơn nghỉ phép

### 👥 Quản lý nhân viên

- ✅ CRUD nhân viên với thông tin đầy đủ
- ✅ Phân quyền theo vai trò
- ✅ Tìm kiếm và lọc nhân viên
- ✅ Gán nhân viên vào phòng ban

### 🏢 Quản lý phòng ban

- ✅ CRUD phòng ban
- ✅ Gán Team Lead cho phòng ban
- ✅ Quản lý thành viên phòng ban
- ✅ Cơ cấu tổ chức linh hoạt

### 📅 Quản lý nghỉ phép thông minh

- ✅ Gửi đơn nghỉ phép với nhiều loại (phép năm, ốm đau, việc riêng, thai sản)
- ✅ Workflow duyệt đa cấp (Team Lead → HR)
- ✅ Theo dõi số ngày phép còn lại
- ✅ Lịch sử nghỉ phép chi tiết
- ✅ Thống kê và báo cáo

### 🤖 AI Agent thông minh

- ✅ **Chatbot tự nhiên**: Hiểu tiếng Việt, tự động gọi API
- ✅ **Intent Recognition**: Tự động nhận diện ý định người dùng
- ✅ **LangGraph Workflow**: Xử lý approval phức tạp với risk assessment
- ✅ **Smart Approval**: Tự động tìm đơn nghỉ phép cần duyệt
- ✅ **Conflict Detection**: Phát hiện xung đột lịch nghỉ phép
- ✅ **Escalation Logic**: Tự động chuyển escalate khi cần thiết

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  Django Backend │    │   AI Agent      │
│   (Port 3000)   │────│   (Port 8000)   │────│  (Port 9000)    │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • REST APIs     │    │ • FastAPI       │
│ • Employee Mgmt │    │ • Authentication│    │ • LangChain     │
│ • Leave Mgmt    │    │ • Authorization │    │ • LangGraph     │
│ • Departments   │    │ • Business Logic│    │ • Gemini AI     │
│ • AI Chat       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   + Redis Cache │
                    │                 │
                    │ • User Data     │
                    │ • Leave Records │
                    │ • Departments   │
                    │ • Sessions      │
                    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend

- **Framework**: Django 4.2.7 + Django REST Framework 3.14.0
- **Database**: PostgreSQL với Redis caching
- **Authentication**: JWT (Simple JWT)
- **API Documentation**: drf-yasg (Swagger)
- **Permissions**: Custom role-based permissions

### Frontend

- **Framework**: React 18
- **HTTP Client**: Axios
- **Routing**: React Router DOM
- **UI**: Bootstrap + Custom CSS
- **State Management**: React Hooks

### AI Agent

- **Framework**: FastAPI
- **LLM**: Google Gemini 1.5 Pro
- **Orchestration**: LangGraph
- **Chain Management**: LangChain
- **Intent Recognition**: Custom NLP pipeline

### DevOps

- **Environment**: python-decouple
- **CORS**: django-cors-headers
- **Static Files**: WhiteNoise
- **Process Management**: Uvicorn, Gunicorn

## 🚀 Cài đặt và chạy dự án

### Yêu cầu hệ thống

- Python 3.11+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+

### 1. Cài đặt Backend (Django)

```bash
# Clone repository
git clone <repository-url>
cd human-resource-ai-agent

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Tạo file .env
cp .env.example .env
# Cập nhật thông tin database và API keys trong .env

# Chạy migrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Tạo dữ liệu mẫu (optional)
python create_sample_data.py

# Chạy Django server
python manage.py runserver
```

### 2. Cài đặt Frontend (React)

```bash
# Di chuyển vào thư mục frontend
cd hrm-frontend

# Cài đặt dependencies
npm install

# Chạy development server
npm start
```

### 3. Cài đặt AI Agent (FastAPI)

```bash
# Di chuyển vào thư mục ai_agent
cd ai_agent

# Cài đặt dependencies cho AI agent
pip install fastapi uvicorn langchain langchain-google-genai langgraph pydantic

# Tạo file .env và thêm GEMINI_API_KEY
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env

# Chạy FastAPI server
uvicorn ai_backend:app --reload --port 9000
```

### 4. Cấu hình Database

```bash
# Tạo PostgreSQL database
sudo -u postgres psql
CREATE DATABASE hr_management;
CREATE USER hr_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hr_management TO hr_user;
\q

# Khởi động Redis
sudo systemctl start redis-server
```

## 🎯 Hướng dẫn sử dụng

### Đăng nhập hệ thống

Sau khi chạy `create_sample_data.py`, bạn có thể sử dụng các tài khoản test:

| Vai trò     | Username        | Password      | Mô tả               |
| ----------- | --------------- | ------------- | ------------------- |
| HR Manager  | `hr_manager`    | `password123` | Toàn quyền hệ thống |
| Tech Lead   | `tech_lead`     | `password123` | Quản lý team IT     |
| Sales Lead  | `sales_lead`    | `password123` | Quản lý team Sales  |
| Developer   | `dev1` / `dev2` | `password123` | Nhân viên IT        |
| Sales Staff | `sales1`        | `password123` | Nhân viên Sales     |

### Sử dụng AI Chatbot

AI Agent hỗ trợ các câu lệnh tự nhiên bằng tiếng Việt:

#### 📋 Xem thông tin

```
"Xem profile của tôi"
"Danh sách nhân viên"
"Có bao nhiều phòng ban?"
"Xem số ngày phép còn lại"
```

#### 📝 Quản lý nghỉ phép

```
"Xin nghỉ ốm từ 15/01 đến 17/01 vì bị cảm"
"Xem lịch sử nghỉ phép"
"Có đơn nào đang chờ duyệt không?"
```

#### ✅ Duyệt đơn (Team Lead/HR)

```
"Duyệt đơn của Nguyễn Văn A"
"Duyệt đơn ID 123"
"Từ chối đơn nghỉ phép ID 456"
"Danh sách đơn cần duyệt"
```

#### 👥 Quản lý nhân viên (HR)

```
"Thêm nhân viên mới"
"Xóa nhân viên ID 789"
"Chuyển Nguyễn Văn B sang phòng IT"
```

### Complex Approval Workflow

AI Agent sử dụng **LangGraph** để xử lý các tình huống phức tạp:

- 🔍 **Risk Assessment**: Đánh giá rủi ro khi nhiều người cùng nghỉ
- ⚠️ **Conflict Detection**: Phát hiện xung đột lịch nghỉ phép
- 📊 **Business Rules**: Áp dụng quy tắc nghiệp vụ tự động
- 🚨 **Auto Escalation**: Chuyển lên cấp cao khi cần thiết

## 🔧 API Documentation

### Django REST API Endpoints

| Endpoint                            | Method                 | Mô tả             | Quyền         |
| ----------------------------------- | ---------------------- | ----------------- | ------------- |
| `/api/users/`                       | GET, POST, PUT, DELETE | Quản lý nhân viên | HR, Team Lead |
| `/api/departments/`                 | GET, POST, PUT, DELETE | Quản lý phòng ban | HR, Team Lead |
| `/api/leave-requests/`              | GET, POST              | Đơn nghỉ phép     | All           |
| `/api/leave-requests/{id}/approve/` | POST                   | Duyệt đơn         | Team Lead, HR |
| `/api/leave-requests/{id}/deny/`    | POST                   | Từ chối đơn       | Team Lead, HR |
| `/api/leave-balances/`              | GET, PUT               | Số ngày phép      | All           |
| `/api/leave-types/`                 | GET, POST, PUT, DELETE | Loại nghỉ phép    | HR            |
| `/api/me/`                          | GET                    | Thông tin cá nhân | All           |

### AI Agent API

| Endpoint | Method | Mô tả             |
| -------- | ------ | ----------------- |
| `/chat`  | POST   | Chat với AI Agent |

#### Request format:

```json
{
  "user_id": 1,
  "role": "employee",
  "message": "Xin nghỉ ốm ngày mai",
  "token": "jwt_token_here"
}
```

## 🔐 Hệ thống phân quyền

### View-level Permissions

```python
# Ví dụ: Chỉ HR mới được thêm nhân viên
"add_employee": PermissionRule(
    allowed_roles=["hr"],
    description="Chỉ HR mới được thêm nhân viên"
)
```

### Object-level Permissions

```python
# Ví dụ: Team Lead chỉ duyệt đơn của team member
"approve_leave": PermissionRule(
    allowed_roles=["team_lead", "hr"],
    object_level_check="team_member_or_hr",
    description="Team Lead chỉ duyệt đơn của team member, HR duyệt tất cả"
)
```

## 🧪 Testing

### Chạy test Django

```bash
python manage.py test
```

### Test AI Agent workflow

```bash
cd ai_agent
python test_langgraph_workflow.py
```

### Test End-to-End

```bash
python test_end_to_end.py
```

## 📁 Cấu trúc thư mục

```
human-resource-ai-agent/
├── ai_agent/                     # AI Agent (FastAPI)
│   ├── ai_backend.py            # FastAPI main app
│   ├── intent_api_mapping.py    # Intent processing & API calls
│   ├── langgraph_approval_workflow.py  # Complex approval logic
│   ├── schema_registry.py       # API schemas & permissions
│   └── constants.py             # Mapping constants
├── apps/                        # Django apps
│   ├── users/                   # User management
│   ├── departments/             # Department management
│   └── leave_management/        # Leave management
├── hrm-frontend/                # React frontend
│   ├── src/
│   │   ├── pages/              # React pages
│   │   ├── api/                # API utilities
│   │   └── services/           # Business logic
│   └── public/
├── hr_management/               # Django project settings
│   ├── config/                 # Environment-specific settings
│   ├── settings.py
│   └── urls.py
├── requirements.txt             # Python dependencies
├── manage.py                   # Django management
└── README.md                   # Documentation
```

## 🌟 Tính năng nâng cao

### 1. Smart Leave Approval

- Tự động tìm đơn nghỉ phép cần duyệt
- Hiển thị danh sách interactive để chọn
- Support multi-criteria filtering

### 2. LangGraph Complex Workflow

- Multi-agent decision making
- Risk assessment với scoring
- Business rules engine
- Automatic escalation

### 3. Intelligent Entity Extraction

- Vietnamese language support
- Context-aware field mapping
- Auto-completion for partial information

### 4. Role-based Data Filtering

- Dynamic queryset based on user role
- Object-level permission checking
- Secure data isolation

## 🚀 Triển khai Production

### Environment Variables (.env)

```bash
# Database
DB_NAME=hr_management
DB_USER=hr_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Django
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# AI
GEMINI_API_KEY=your_gemini_api_key_here
```

### Docker Deployment (Optional)

```bash
# Build và chạy với Docker Compose
docker-compose up -d
```

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push branch: `git push origin feature/new-feature`
5. Tạo Pull Request

## 📞 Hỗ trợ

- **Documentation**: `/swagger/` - API documentation
- **Admin Panel**: `/admin/` - Django admin
- **Logs**: `logs/django.log` - Application logs

## 📜 License

MIT License - Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

---

⭐ **Tạo bởi**: AI-powered HR Management System với LangGraph  
🔗 **Tech Stack**: Django + React + FastAPI + LangGraph + Gemini AI
