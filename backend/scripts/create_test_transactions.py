from decimal import Decimal
import random
from django.utils import timezone
from wallet.models import User
from user.models import WalletTransaction

# Test data
TRANSACTION_AMOUNTS = [
    100000,  # 100,000 تومان
    250000,  # 250,000 تومان
    500000,  # 500,000 تومان
    1000000,  # 1,000,000 تومان
    2000000,  # 2,000,000 تومان
]

DEPOSIT_DESCRIPTIONS = [
    'شارژ کیف پول',
    'واریز از درگاه بانکی',
    'هدیه ثبت نام',
    'پاداش معرفی دوستان',
    'بازگشت وجه از سفارش لغو شده',
]

PURCHASE_DESCRIPTIONS = [
    'خرید دوره آموزش تحلیل تکنیکال',
    'خرید پکیج جامع ارزهای دیجیتال',
    'ثبت نام در وبینار تخصصی',
    'خرید اشتراک ویژه',
    'شرکت در دوره مقدماتی بورس',
]

def create_test_transactions():
    # Get all test users
    users = User.objects.filter(phone_number__in=['09121111111', '09122222222', '09123333333'])
    
    for user in users:
        # Create 3-5 deposits for each user
        for _ in range(random.randint(3, 5)):
            amount = Decimal(random.choice(TRANSACTION_AMOUNTS))
            description = random.choice(DEPOSIT_DESCRIPTIONS)
            
            WalletTransaction.objects.create(
                user=user,
                amount=amount,
                transaction_type='deposit',
                description=description,
                status='completed'
            )
            user.add_to_wallet(amount)
        
        # Create 2-4 purchases for each user
        for _ in range(random.randint(2, 4)):
            amount = Decimal(random.choice(TRANSACTION_AMOUNTS[:3]))  # Using smaller amounts for purchases
            description = random.choice(PURCHASE_DESCRIPTIONS)
            
            if user.wallet_balance >= amount:
                WalletTransaction.objects.create(
                    user=user,
                    amount=amount,
                    transaction_type='purchase',
                    description=description,
                    status='completed'
                )
                user.deduct_from_wallet(amount)

if __name__ == '__main__':
    create_test_transactions() 