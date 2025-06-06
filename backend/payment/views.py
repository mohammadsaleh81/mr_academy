from rest_framework.views import APIView
from rest_framework.response import Response
from payment.gateway.zarinpal import *
from payment.models import  Payment


from datetime import datetime
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    agent = request.META.get('HTTP_USER_AGENT', ''),
    get_params = request.GET.dict()
    post_params = request.POST.dict() if request.method == 'POST' else {}



    return {
        'ip': ip,
        'agent': agent,
        'get': get_params,
        'post': post_params
    }



class CreatePayment(APIView):
    def post(self, request):
        test_amount = request.data.get("amount")

        test_description =  request.data.get("des", "test")
        test_email =  request.data.get("email", "tes")
        test_mobile =  request.data.get("mobile", "tes")


        payment_instance = Payment()

        result = send_payment_request(
            amount=int(test_amount),
            description=test_description,
            email=test_email,
            mobile=test_mobile
        )
        req_data = get_client_ip(request)
        authority = result["data"]["authority"]
        payment_url = settings.ZP_API_STARTPAY + authority
        req_data.update({"url": payment_url})
        payment_instance.authority = authority
        payment_instance.user = request.user
        payment_instance.amount = int(test_amount)
        payment_instance.ip_address = req_data["ip"]
        payment_instance.extra = req_data
        payment_instance.save()

        return Response({"url": payment_url})




class VerifyView(APIView):
    def get(self, request):
        authority = request.GET.get("Authority")
        pay_status = request.GET.get("Status")

        instance = Payment.objects.filter(authority=authority).first()

        if not  instance:
            return  Response({'status': 'failed', })

        if pay_status !=  'OK':
            instance.status = 'refunded'

        else:
            instance.status = 'successful'

        instance.done_at = datetime.now()
        instance.save()


        verify = send_verify(authority=instance.authority, amount=int(instance.amount))
        data = verify.get('data', None)
        if data:
            instance.card_hash = data.get('card_hash', '')
            instance.card_pan = data.get('card_pan', '')
            instance.ref_id = data.get('ref_id', '')
            instance.fee_type = data.get('fee_type', '')
            instance.shaparak_fee = data.get('shaparak_fee', '')

            extra = instance.extra
            extra.update({'verify': verify})
            instance.extra = extra
            instance.save()


        return Response(verify)


