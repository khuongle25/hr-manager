from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('hr', 'HR'),
        ('team_lead', 'Team Lead'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey('departments.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"
