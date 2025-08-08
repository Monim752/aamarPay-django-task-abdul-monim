from rest_framework import serializers
from .models import FileUpload, PaymentTransaction, ActivityLog

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['id','user','file','filename','upload_time','status','word_count']
        read_only_fields = ['id','user','upload_time','status','word_count']

    def create(self, validated_data):
        user = self.context['request'].user
        file = validated_data['file']
        filename = file.name
        file_model = FileUpload.objects.create(user=user, file=file, filename=filename, status='processing')
        # Trigger celery
        from .tasks import process_file_upload
        process_file_upload.delay(file_model.id)
        return file_model

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = '__all__'
        read_only_fields = ['gateway_response', 'timestamp']

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'
