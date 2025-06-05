from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wallet.models import Wallet

User = get_user_model()


class Command(BaseCommand):
    help = 'Create missing wallets for users who do not have them'

    def handle(self, *args, **options):
        users_without_wallets = User.objects.filter(wallet__isnull=True)
        count = users_without_wallets.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('All users already have wallets.')
            )
            return

        self.stdout.write(f'Found {count} users without wallets. Creating...')
        
        created_count = 0
        for user in users_without_wallets:
            try:
                Wallet.objects.create(user=user)
                created_count += 1
                self.stdout.write(f'Created wallet for user: {user.phone_number}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create wallet for user {user.phone_number}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} wallets.')
        ) 