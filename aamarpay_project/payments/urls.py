from django.urls import path
from .views import InitiatePaymentView, PaymentSuccessView, FileUploadView, FileListView, ActivityListView, \
    TransactionListView, dashboard_view

urlpatterns = [
    path('api/initiate-payment/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('api/payment/success/', PaymentSuccessView.as_view(), name='payment-success'),  # gateway callback
    path('api/upload/', FileUploadView.as_view(), name='file-upload'),
    path('api/files/', FileListView.as_view(), name='files-list'),
    path('api/activity/', ActivityListView.as_view(), name='activity-list'),
    path('api/transactions/', TransactionListView.as_view(), name='transactions-list'),
    path('dashboard/', dashboard_view, name='dashboard'),
]
