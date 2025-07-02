from django.db import models
from apps.users.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    lead = models.ManyToManyField(User, blank=True, related_name='lead_departments')
    members = models.ManyToManyField(User, related_name='departments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
