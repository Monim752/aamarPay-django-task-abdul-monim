from django.db import models
from django.conf import settings

class FileUpload(models.Model):
    STATUS_CHOICES = (
        ('processing', 'processing'),
        ('completed', 'completed'),
        ('failed', 'failed'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    upload_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    word_count = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.filename} ({self.user})"


class PaymentTransaction(models.Model):
    STATUS_CHOICES = (
        ('initiated','initiated'),
        ('successful','successful'),
        ('failed','failed'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=128, unique=True)  # mer_txnid
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    gateway_response = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.user} - {self.status}"


class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    metadata = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"

