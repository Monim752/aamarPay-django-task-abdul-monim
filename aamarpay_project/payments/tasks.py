from celery import shared_task
from .models import FileUpload, ActivityLog
from docx import Document


@shared_task
def process_file_upload(file_upload_id):
    file_model = FileUpload.objects.get(pk=file_upload_id)
    path = file_model.file.path
    try:
        if path.lower().endswith('.txt'):
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:  # .docx
            doc = Document(path)
            text = "\n".join([p.text for p in doc.paragraphs])

        # naive word count by whitespace split
        words = [w for w in text.split() if w.strip()]
        wc = len(words)

        file_model.word_count = wc
        file_model.status = 'completed'
        file_model.save()

        ActivityLog.objects.create(
            user=file_model.user,
            action='file_processed',
            metadata={'file_upload_id': file_model.id, 'word_count': wc}
        )
    except Exception as e:
        file_model.status = 'failed'
        file_model.save()
        ActivityLog.objects.create(
            user=file_model.user,
            action='file_processing_failed',
            metadata={'file_upload_id': file_model.id, 'error': str(e)}
        )
        raise
