import uuid
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
import requests

from .models import PaymentTransaction, FileUpload, ActivityLog
from .serializers import FileUploadSerializer, PaymentTransactionSerializer, ActivityLogSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class InitiatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        amount = "100.00"  # per spec
        mer_txnid = str(uuid.uuid4())[:32]  # max 32 chars
        # create initiated transaction
        tx = PaymentTransaction.objects.create(
            user=user, transaction_id=mer_txnid, amount=amount, status='initiated'
        )

        payload = {
            "store_id": settings.AAMARPAY_STORE_ID,
            "tran_id": mer_txnid,          # merchant transaction id sent as tran_id
            "success_url": request.build_absolute_uri('/api/payment/success/'),
            "fail_url": request.build_absolute_uri('/api/payment/fail/'),
            "cancel_url": request.build_absolute_uri('/'),
            "amount": amount,
            "currency": "BDT",
            "signature_key": settings.AAMARPAY_SIGNATURE_KEY,
            "desc": "File upload fee",
            "cus_name": user.get_full_name() or user.username,
            "cus_email": user.email or '',
            "cus_phone": "01700000000",
            "type": "json"
        }

        resp = requests.post(settings.AAMARPAY_ENDPOINT, json=payload, headers={"Content-Type":"application/json"})
        data = resp.json()
        # expected: {"result":"true","payment_url":"https://..."}
        if data.get('result') in ['true', True] and data.get('payment_url'):
            return Response({"payment_url": data['payment_url']})
        else:
            return Response({"error":"payment initiation failed","detail":data}, status=status.HTTP_400_BAD_REQUEST)


# The callback aamarPay hits; allow both GET/POST; no auth (aamarPay will call it)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # the gateway will forward data; but we do authoritative verification using Search Transection API
        mer_txnid = request.data.get('mer_txnid') or request.data.get('mer_txnid')
        if not mer_txnid:
            return Response({"error":"missing mer_txnid"}, status=status.HTTP_400_BAD_REQUEST)

        # find our initiated transaction
        try:
            tx = PaymentTransaction.objects.get(transaction_id=mer_txnid)
        except PaymentTransaction.DoesNotExist:
            return Response({"error":"unknown transaction"}, status=status.HTTP_404_NOT_FOUND)

        # Verify with aamarPay search API
        params = {
            "request_id": mer_txnid,
            "store_id": settings.AAMARPAY_STORE_ID,
            "signature_key": settings.AAMARPAY_SIGNATURE_KEY,
            "type": "json"
        }
        r = requests.get(settings.AAMARPAY_TRX_CHECK, params=params)
        data = r.json()
        tx.gateway_response = data
        # status_code '2' => successful per docs
        if str(data.get('status_code')) == '2' or str(data.get('pay_status')).lower() == 'successful':
            tx.status = 'successful'
            tx.save()
            ActivityLog.objects.create(user=tx.user, action='payment_success', metadata={'mer_txnid': mer_txnid, 'gateway': data})
            # Optionally redirect user to dashboard
            return Response({"status":"ok","message":"payment verified"}, status=status.HTTP_200_OK)
        else:
            tx.status = 'failed'
            tx.save()
            ActivityLog.objects.create(user=tx.user, action='payment_failed', metadata={'mer_txnid': mer_txnid, 'gateway': data})
            return Response({"status":"failed","gateway": data}, status=status.HTTP_400_BAD_REQUEST)

    # Sometimes gateway redirects via GET; support that too
    def get(self, request):
        return self.post(request)


# Upload endpoint
class FileUploadView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        paid = PaymentTransaction.objects.filter(user=user, status='successful').exists()
        if not paid:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You must complete payment before uploading files.")
        serializer.save(user=user)


# lists
class FileListView(generics.ListAPIView):
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return FileUpload.objects.filter(user=self.request.user).order_by('-upload_time')

class ActivityListView(generics.ListAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user).order_by('-timestamp')

class TransactionListView(generics.ListAPIView):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return PaymentTransaction.objects.filter(user=self.request.user).order_by('-timestamp')


@login_required
def dashboard_view(request):
    paid = PaymentTransaction.objects.filter(user=request.user, status='successful').exists()
    files = FileUpload.objects.filter(user=request.user).order_by('-upload_time')
    return render(request, 'dashboard.html', {'paid': paid, 'files': files})