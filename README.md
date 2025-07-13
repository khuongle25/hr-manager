# Ứng dụng Quản lý Nhân lực với AI Agent

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

