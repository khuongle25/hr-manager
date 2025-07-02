from apps.users.models import User
from apps.departments.models import Department

count = 0
for user in User.objects.exclude(department=None):
    dept = user.department
    if dept:
        dept.members.add(user)
        dept.save()
        count += 1
print(f"Đã đồng bộ xong members cho các phòng ban. Tổng số user được thêm: {count}")