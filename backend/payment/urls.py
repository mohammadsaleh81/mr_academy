from django.urls import path
from payment.views import CreatePayment, VerifyView

urlpatterns = [
    path('create/', CreatePayment.as_view(), name='create_payment'),
    path('verify/', VerifyView.as_view(), name='verify_payment'),

]