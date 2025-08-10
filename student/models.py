from django.db import models
from django.utils import timezone

class Teacher(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=256)
    salt = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Student(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    marks = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "subject")

    def __str__(self):
        return f"{self.name} - {self.subject}"

class SessionToken(models.Model):
    token = models.CharField(max_length=128, unique=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() >= self.expires_at

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ("INSERT", "INSERT"),
        ("UPDATE", "UPDATE"),
        ("DELETE", "DELETE"),
    )
    teacher = models.ForeignKey(Teacher, null=True, on_delete=models.SET_NULL)
    student = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    field = models.CharField(max_length=100, null=True, blank=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
