from rest_framework.views import APIView
from rest_framework.response import Response
from payments.zar import *


class CreatePayment(APIView):
    def post(self, request):
        test_amount = request.data.get("amount")

        test_description = "Test Transaction for a product"
        test_email = "customer@example.com"
        test_mobile = "09123456789"

        result = send_payment_request(
            amount=int(test_amount),
            description=test_description,
            email=test_email,
            mobile=test_mobile
        )
        authority = result["data"]["authority"]
        print("create      =========>>>>     ")
        print(authority)
        print("_________________________________")
        payment_url = settings.ZP_API_STARTPAY + authority
        return Response({"url": payment_url})




class VerifyView(APIView):
    def get(self, request):
        authority = request.GET.get("Authority", None)
        test_amount = 1000
        test_description = "Test Transaction for a product"
        test_email = "customer@example.com"
        test_mobile = "09123456789"

        print("verify      =========>>>>     ")
        print(authority)
        print("*********************************")


        verify = send_verify(test_amount, authority)
        return Response({"data": verify})


    def post(self, request):
        test_amount = 1000
        test_description = "Test Transaction for a product"
        test_email = "customer@example.com"
        test_mobile = "09123456789"

        result = send_payment_request(
            amount=test_amount,
            description=test_description,
            email=test_email,
            mobile=test_mobile
        )

        authority = result["data"]["authority"]
        payment_url = settings.ZP_API_STARTPAY + authority
        print(payment_url)

        verify = send_verify(test_amount, authority)




        return Response({"data": verify})

