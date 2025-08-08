from django.contrib import admin
from .models import FileUpload, PaymentTransaction, ActivityLog

class BaseReadOnlyAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # staff can view but not change; superuser allowed.
        return request.user.is_superuser

@admin.register(FileUpload)
class FileUploadAdmin(BaseReadOnlyAdmin):
    list_display = ('id','user','filename','upload_time','status','word_count')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(BaseReadOnlyAdmin):
    list_display = ('transaction_id','user','amount','status','timestamp')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user','action','timestamp')
    readonly_fields = ('user','action','metadata','timestamp')
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
