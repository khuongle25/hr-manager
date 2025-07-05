# Ứng dụng Quản lý Nhân lực với AI Agent

## Mô tả dự án

Ứng dụng web quản lý nhân lực dành cho HR, Team Lead và nhân viên trong công ty, với AI Agent hỗ trợ cho cả 3 role. Ứng dụng tập trung vào quản lý xin nghỉ phép và các tác vụ liên quan.

## Công nghệ sử dụng

- **Backend**: Django 4.2+ (chuẩn doanh nghiệp)
- **Database**: PostgreSQL
- **AI Framework**: LangChain
- **Cache & Session**: Redis
- **Frontend**: Django Templates + Bootstrap
- **Authentication**: Django Allauth
- **API**: Django REST Framework

## Kế hoạch học tập và phát triển

### Phase 1: Thiết lập môi trường và cấu trúc cơ bản (Tuần 1)

#### 1.1 Thiết lập môi trường

- [ ] Cài đặt Python, PostgreSQL, Redis
- [ ] Tạo virtual environment
- [ ] Cài đặt Django và các dependencies
- [ ] Cấu hình Docker (tùy chọn)

#### 1.2 Cấu trúc dự án Django

- [ ] Tạo project Django với cấu trúc chuẩn doanh nghiệp
- [ ] Cấu hình settings cho development/production
- [ ] Thiết lập PostgreSQL connection
- [ ] Cấu hình Redis cho cache và session
- [ ] Thiết lập logging và monitoring

#### 1.3 Authentication và Authorization

- [ ] Cài đặt Django Allauth
- [ ] Tạo custom User model
- [ ] Thiết lập role-based permissions (HR, Team Lead, Employee)
- [ ] Tạo login/logout views

### Phase 2: Database Design và Models (Tuần 2)

#### 2.1 Thiết kế Database Schema

- [ ] Thiết kế ERD cho hệ thống
- [ ] Tạo models cho:
  - User/Employee
  - Department
  - Leave Request
  - Leave Type
  - Leave Balance
  - Notification
- [ ] Thiết lập relationships và constraints

#### 2.2 Database Operations

- [ ] Tạo và chạy migrations
- [ ] Thiết lập database indexes
- [ ] Tạo initial data (fixtures)
- [ ] Thiết lập database backup strategy

### Phase 3: Core Business Logic (Tuần 3)

#### 3.1 Leave Management System

- [ ] Tạo views cho CRUD operations
- [ ] Implement leave request workflow
- [ ] Tạo approval system cho Team Lead và HR
- [ ] Implement leave balance calculation
- [ ] Tạo notification system

#### 3.2 User Management

- [ ] Employee profile management
- [ ] Department management
- [ ] Team assignment
- [ ] Role-based dashboard

### Phase 4: AI Agent với LangChain (Tuần 4)

#### 4.1 Thiết lập LangChain

- [ ] Cài đặt và cấu hình LangChain
- [ ] Thiết lập Gemini/LLM connection
- [ ] Tạo base AI agent structure

#### 4.2 AI Agent Features

- [ ] **HR Agent**: Hỗ trợ quản lý nhân sự, phân tích dữ liệu
- [ ] **Team Lead Agent**: Hỗ trợ quản lý team, approval decisions
- [ ] **Employee Agent**: Hỗ trợ nhân viên, trả lời câu hỏi
- [ ] Tích hợp với database để truy vấn thông tin

#### 4.3 AI Agent Capabilities

- [ ] Natural language processing cho leave requests
- [ ] Automated approval suggestions
- [ ] Data analysis và reporting
- [ ] FAQ và support system

### Phase 5: Redis Integration (Tuần 5)

#### 5.1 Caching Strategy

- [ ] Cache user sessions
- [ ] Cache frequently accessed data
- [ ] Cache AI agent responses
- [ ] Implement cache invalidation

#### 5.2 Performance Optimization

- [ ] Database query optimization
- [ ] Redis caching cho API responses
- [ ] Session management với Redis
- [ ] Background task processing

### Phase 6: API và Frontend (Tuần 6)

#### 6.1 REST API

- [ ] Tạo Django REST Framework API
- [ ] API authentication và permissions
- [ ] API documentation với Swagger
- [ ] API testing

#### 6.2 Frontend Development

- [ ] Responsive UI với Bootstrap
- [ ] Dashboard cho từng role
- [ ] Leave request forms
- [ ] Real-time notifications

### Phase 7: Testing và Deployment (Tuần 7)

#### 7.1 Testing

- [ ] Unit tests cho models và views
- [ ] Integration tests cho AI agents
- [ ] API testing
- [ ] Performance testing

#### 7.2 Deployment

- [ ] Production environment setup
- [ ] Database migration strategy
- [ ] CI/CD pipeline
- [ ] Monitoring và logging

## Cấu trúc thư mục dự án

```
human-resource-ai-agent/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── docker-compose.yml (tùy chọn)
├── hr_management/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/
│   ├── leave_management/
│   ├── departments/
│   └── ai_agents/
├── static/
├── templates/
├── media/
├── tests/
└── docs/
```

## Học tập theo từng phase

### Phase 1: Nền tảng

- **Django**: Project structure, settings, middleware
- **PostgreSQL**: Connection, basic operations
- **Redis**: Installation, basic commands

### Phase 2: Database

- **Django ORM**: Models, relationships, migrations
- **PostgreSQL**: Advanced queries, indexes, constraints

### Phase 3: Business Logic

- **Django**: Views, forms, permissions
- **PostgreSQL**: Complex queries, transactions

### Phase 4: AI Integration

- **LangChain**: Agents, chains, tools
- **LLM Integration**: OpenAI API, prompt engineering

### Phase 5: Performance

- **Redis**: Caching strategies, session management
- **Django**: Performance optimization

### Phase 6: API & Frontend

- **DRF**: Serializers, viewsets, authentication
- **Frontend**: Templates, JavaScript, AJAX

### Phase 7: Production

- **Deployment**: Gunicorn, Nginx, environment management
- **Testing**: Django testing framework, pytest

## Kết quả mong đợi

Sau khi hoàn thành dự án, bạn sẽ có:

1. Hiểu biết sâu về Django enterprise development
2. Kinh nghiệm với PostgreSQL trong production
3. Kỹ năng xây dựng AI agents với LangChain
4. Kiến thức về Redis caching và session management
5. Một ứng dụng hoàn chỉnh có thể deploy production

## Bắt đầu

Để bắt đầu, hãy chạy lệnh sau để tạo cấu trúc dự án cơ bản:

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy migrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Chạy development server
python manage.py runserver
```
uvicorn ai_backend:app --reload --port 9000

Bạn có thể đăng nhập bằng các tài khoản sau để kiểm tra phân quyền và giao diện:
HR Manager: hr_manager / password123
Tech Lead: tech_lead / password123
Sales Lead: sales_lead / password123
Dev 1: dev1 / password123
Dev 2: dev2 / password123
Sales 1: sales1 / password123
Accountant: accountant / password123
