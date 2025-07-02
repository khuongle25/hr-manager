from django.db import models
from apps.users.models import User
from apps.departments.models import Department

class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    max_days_per_year = models.PositiveIntegerField(default=12)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    APPROVAL_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_leaves')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    team_lead_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='pending')
    hr_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='pending')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"

class LeaveBalance(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)

    class Meta:
        unique_together = ('employee', 'leave_type')
        ordering = ['employee__first_name', 'employee__last_name', 'leave_type__name']

    def __str__(self):
        return f"{self.employee} - {self.leave_type}: {self.balance} days"