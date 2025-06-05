import requests
import json

MERCHANT_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # Replace with your actual Merchant ID
ZP_API_REQUEST = "https://payment.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://payment.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://payment.zarinpal.com/pg/StartPay/"

# This will be your callback URL that Zarinpal redirects to after payment
CALLBACK_URL = 'http://localhost:8000/verify/' # Make sure this is a URL Zarinpal can reach

def send_payment_request(amount, description, mobile=None, email=None, order_id=None):
    """
    Step 1: Request a payment authority from Zarinpal.
    """
    payload = {
        "merchant_id": MERCHANT_ID,
        "amount": amount,  # Amount in Tomans (or Rials, specify with 'currency')
        "callback_url": CALLBACK_URL,
        "description": description,
        "metadata": {}
    }

    if mobile:
        payload["metadata"]["mobile"] = mobile
    if email:
        payload["metadata"]["email"] = email
    # if order_id: # The documentation mentions order_id in metadata, adjust if needed
    #     payload["metadata"]["order_id"] = order_id


    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        response = requests.post(ZP_API_REQUEST, data=json.dumps(payload), headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()

        if result.get("data") and result["data"].get("code") == 100 and result["data"].get("authority"):
            authority = result["data"]["authority"]
            payment_url = ZP_API_STARTPAY + authority
            print(f"Payment request successful. Authority: {authority}")
            print(f"Redirect user to: {payment_url}")
            return authority, payment_url
        elif result.get("errors") and result["errors"].get("code"):
            error_code = result["errors"]["code"]
            error_message = result["errors"].get("message", "Unknown error")
            print(f"Error requesting payment: Code {error_code} - {error_message}")
            return None, None
        else:
            print(f"Unknown error or malformed response: {result}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, None
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response: {response.text}")
        return None, None

def verify_payment(authority, amount):
    """
    Step 3: Verify the payment after Zarinpal redirects back to your callback_url.
    """
    payload = {
        "merchant_id": MERCHANT_ID,
        "authority": authority,
        "amount": amount # Amount in Tomans (or Rials, must match the request)
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        response = requests.post(ZP_API_VERIFY, data=json.dumps(payload), headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()

        if result.get("data") and result["data"].get("code") == 100:
            ref_id = result["data"].get("ref_id")
            print(f"Payment verified successfully. Ref ID: {ref_id}")
            # Here, you should update your database, mark the order as paid, etc.
            return True, ref_id, result.get("data") # Return the full data for more details if needed
        elif result.get("data") and result["data"].get("code") == 101:
             print(f"Payment was already verified. Ref ID: {result['data'].get('ref_id')}")
             # This means the transaction was successful and verified before.
             return True, result['data'].get('ref_id'), result.get("data")
        elif result.get("errors") and result["errors"].get("code"):
            error_code = result["errors"]["code"]
            error_message = result["errors"].get("message", "Unknown error during verification")
            print(f"Payment verification failed: Code {error_code} - {error_message}")
            return False, None, result.get("errors")
        else:
            print(f"Unknown error or malformed verification response: {result}")
            return False, None, result

    except requests.exceptions.RequestException as e:
        print(f"Verification request failed: {e}")
        return False, None, {"message": str(e)}
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response during verification: {response.text}")
        return False, None, {"message": f"JSON decode error: {response.text}"}

# --- Example Usage ---
if __name__ == "__main__":
    test_amount = 1100  # Example amount in Tomans
    test_description = "Test Transaction for a product"
    test_email = "customer@example.com"
    test_mobile = "09123456789"

    print("--- Step 1: Requesting Payment ---")
    authority_token, payment_redirect_url = send_payment_request(
        amount=test_amount,
        description=test_description,
        email=test_email,
        mobile=test_mobile
    )

    if authority_token and payment_redirect_url:
        print(f"\n--- Step 2: User Interaction ---")
        print(f"Please redirect the user to the following URL to complete payment:")
        print(payment_redirect_url)
        print(f"\nAfter payment, Zarinpal will redirect to: {CALLBACK_URL}?Authority={authority_token}&Status=OK (or NOK)")

        # --- Simulate Zarinpal Callback (In a real app, this happens in your callback view) ---
        # For testing, let's assume the user paid successfully and Zarinpal calls back.
        # You would get the 'Authority' and 'Status' from the query parameters of the callback URL.
        print("\n--- Simulating Zarinpal Callback & Step 3: Verifying Payment ---")
        # Simulate a successful callback
        # In a real Django app, you'd get authority from request.GET.get('Authority')
        # and status from request.GET.get('Status')

        # Let's assume the payment was successful for testing verification
        # In a real scenario, you'd check if Status == "OK" from the callback
        mock_status_from_callback = "OK" # or "NOK" if cancelled

        if mock_status_from_callback == "OK" and authority_token:
            is_verified, ref_id, verification_data = verify_payment(authority_token, test_amount)
            if is_verified:
                print(f"\nPayment of {test_amount} Tomans successfully verified!")
                print(f"Transaction Reference ID (Ref ID): {ref_id}")
                print(f"Card Holder: {verification_data.get('card_holder')}") # Example of using more data
                print(f"Card PAN: {verification_data.get('card_pan')}")
                # Save ref_id and update order status in your database
            else:
                print(f"\nPayment verification failed. Details: {verification_data}")
        elif mock_status_from_callback == "NOK":
            print("\nPayment was not successful or was cancelled by the user.")
        else:
            print("\nCallback did not indicate a successful payment or authority token was missing.")
    else:
        print("\nFailed to initiate payment request.")