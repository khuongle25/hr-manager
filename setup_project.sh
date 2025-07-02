#!/bin/bash

# Script thiết lập dự án HR Management với AI Agent
# Chạy script này sau khi clone repository

echo "🚀 Bắt đầu thiết lập dự án HR Management..."

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 chưa được cài đặt. Vui lòng cài đặt Python 3.11+"
    exit 1
fi

# Kiểm tra PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL chưa được cài đặt. Vui lòng cài đặt PostgreSQL"
    exit 1
fi

# Kiểm tra Redis
if ! command -v redis-cli &> /dev/null; then
    echo "❌ Redis chưa được cài đặt. Vui lòng cài đặt Redis"
    exit 1
fi

echo "✅ Các dependencies cơ bản đã được cài đặt"

# Tạo virtual environment
echo "📦 Tạo virtual environment..."
python3 -m venv venv

# Kích hoạt virtual environment
echo "🔧 Kích hoạt virtual environment..."
source venv/bin/activate

# Cài đặt dependencies
echo "📚 Cài đặt Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Tạo file .env từ template
if [ ! -f .env ]; then
    echo "📝 Tạo file .env từ template..."
    cp env.example .env
    echo "⚠️  Vui lòng cập nhật file .env với thông tin database và API keys"
fi

# Tạo cấu trúc thư mục
echo "📁 Tạo cấu trúc thư mục..."
mkdir -p static templates media tests docs logs

# Tạo Django project nếu chưa có
if [ ! -f manage.py ]; then
    echo "🐍 Tạo Django project..."
    django-admin startproject hr_management .
fi

# Tạo apps nếu chưa có
if [ ! -d apps ]; then
    echo "📱 Tạo Django apps..."
    mkdir apps
    cd apps
    django-admin startapp users
    django-admin startapp leave_management
    django-admin startapp departments
    django-admin startapp ai_agents
    cd ..
fi

# Tạo thư mục settings nếu chưa có
if [ ! -d hr_management/settings ]; then
    echo "⚙️  Tạo cấu trúc settings..."
    mkdir -p hr_management/settings
    touch hr_management/settings/__init__.py
fi

echo "✅ Thiết lập cơ bản hoàn tất!"
echo ""
echo "📋 Các bước tiếp theo:"
echo "1. Cập nhật file .env với thông tin database và API keys"
echo "2. Chạy: python manage.py makemigrations"
echo "3. Chạy: python manage.py migrate"
echo "4. Chạy: python manage.py createsuperuser"
echo "5. Chạy: python manage.py runserver"
echo ""
echo "📖 Đọc file docs/PHASE_1_GUIDE.md để biết thêm chi tiết"
echo ""
echo "🎯 Chúc bạn học tập hiệu quả!" 