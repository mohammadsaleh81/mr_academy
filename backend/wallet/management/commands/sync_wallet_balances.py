from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wallet.models import Wallet
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Sync wallet balances between User.wallet_balance and Wallet.balance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--direction',
            choices=['user_to_wallet', 'wallet_to_user'],
            default='user_to_wallet',
            help='Direction of sync: user_to_wallet (default) or wallet_to_user'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes'
        )

    def handle(self, *args, **options):
        direction = options['direction']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        users_with_wallets = User.objects.select_related('wallet').all()
        
        updated_count = 0
        mismatches = []
        
        for user in users_with_wallets:
            try:
                user_balance = user.wallet_balance or Decimal('0')
                wallet_balance = user.wallet.balance
                
                if user_balance != wallet_balance:
                    mismatches.append({
                        'user': user.phone_number,
                        'user_balance': user_balance,
                        'wallet_balance': wallet_balance
                    })
                    
                    if not dry_run:
                        if direction == 'user_to_wallet':
                            # Update wallet balance from user balance
                            user.wallet.balance = user_balance
                            user.wallet.save(update_fields=['balance'])
                            self.stdout.write(f'Updated wallet balance for {user.phone_number}: {wallet_balance} → {user_balance}')
                        else:
                            # Update user balance from wallet balance
                            user.wallet_balance = wallet_balance
                            user.save(update_fields=['wallet_balance'])
                            self.stdout.write(f'Updated user balance for {user.phone_number}: {user_balance} → {wallet_balance}')
                        
                        updated_count += 1
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing user {user.phone_number}: {e}')
                )
        
        if dry_run:
            self.stdout.write(f'\nFound {len(mismatches)} mismatched balances:')
            for mismatch in mismatches:
                self.stdout.write(
                    f"User: {mismatch['user']} - User Balance: {mismatch['user_balance']} - Wallet Balance: {mismatch['wallet_balance']}"
                )
            self.stdout.write(f'\nWould update {len(mismatches)} records if --dry-run was not specified')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully synced {updated_count} wallet balances.')
            ) 