
from django.db import models
from django.db import transaction
from api.models import User  # Assuming User model is imported from your app
from django.conf import settings

from django.core.exceptions import ValidationError

class Bank(models.Model):
    bank_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and Bank.objects.exists():
            raise ValidationError("Only one Bank instance is allowed.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.bank_name

    class Meta:
        verbose_name = "Bank"
        verbose_name_plural = "Banks"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer",blank=True,null=True)
    contact_info = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Customer Profile"
    
    

# class Account(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account', null=False, default=1)  # Provide a default user ID
#     class AccountType(models.TextChoices):
#         SAVINGS = 'SAVINGS', 'Savings'
#         CURRENT = 'CURRENT', 'Current'

#     account_type = models.CharField(max_length=50, choices=AccountType.choices)
#     balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="accounts",null=True,blank=True)
#     # bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name="accounts")

#     def __str__(self):
#         return f"{self.account_type} - {self.id}"

#     def deposit(self, amount):
#         """Deposit amount into the account."""
#         if amount > 0:
#             self.balance += amount
#             self.save()

#     def withdraw(self, amount):
#         """Withdraw amount from the account if sufficient balance exists."""
#         if amount > 0 and self.balance >= amount:
#             self.balance -= amount
#             self.save()
#             return True
#         return False
    


from django.core.exceptions import ValidationError

class Account(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='accounts', 
        null=False, 
        default=1
    )  # Provide a default user ID

    class AccountType(models.TextChoices):
        SAVINGS = 'SAVINGS', 'Savings'
        CURRENT = 'CURRENT', 'Current'

    account_type = models.CharField(max_length=50, choices=AccountType.choices)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="accounts", null=True, blank=True)

    def __str__(self):
        return f"{self.account_type} - {self.id}"

    def clean(self):
        """Ensure that a customer can only have one account of a specific type."""
        if self.account_type == self.AccountType.SAVINGS and Account.objects.filter(
            customer=self.customer, account_type=self.AccountType.SAVINGS
        ).exclude(id=self.id).exists():
            raise ValidationError(f"The customer already has a {self.AccountType.SAVINGS} account.")

    def save(self, *args, **kwargs):
        """Override save to include validation."""
        self.clean()  # Run custom validation
        super().save(*args, **kwargs)

    def deposit(self, amount):
        """Deposit amount into the account."""
        if amount > 0:
            self.balance += amount
            self.save()

    def withdraw(self, amount):
        """Withdraw amount from the account if sufficient balance exists."""
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False



import uuid
from django.utils.timezone import now

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('TRANSFER', 'Transfer'),
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
    ]

    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)  # Unique ID for transaction
    transaction_date = models.DateTimeField(auto_now_add=True)  # Date when transaction was created
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    account_from = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions_from', null=True, blank=True)
    account_to = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions_to', null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, default='completed')

    def __str__(self):
        return f"Transaction {self.transaction_id} of type {self.transaction_type} on {self.transaction_date}"

# class BankCustomer(models.Model): 
#     bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.bank.bank_name} - {self.customer.customer_name}"

#     class Meta:
#         unique_together = ('bank', 'customer')
#         verbose_name = "Bank Customer"
#         verbose_name_plural = "Bank Customers"


# class Deposit(models.Model):
#     account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="deposits")
#     amount = models.DecimalField(max_digits=15, decimal_places=2)
#     transaction_date = models.DateTimeField(auto_now=True)
#     status = models.CharField(max_length=50, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], default='PENDING')
#     # user = models.ForeignKey(User, on_delete=models.CASCADE,default=False)  # Explicit user field

#     def save(self, *args, **kwargs):
#         if self.amount <= 0:
#             raise ValueError("Deposit amount must be greater than zero.")
        
#         # Check if account exists and if the user has access
#         if not Account.objects.filter(id=self.account.id).exists():
#             raise ValueError("Account does not exist.")
        
#         # Ensure the user is the owner of the account
#         # if self.account.user != self.user:
#         #     raise ValueError("Account not found or you don't have access to this account.")
        
#         with transaction.atomic():
#             account = self.account
#             account.deposit(self.amount)  # Update account balance
#             self.status = 'COMPLETED'  # Mark deposit as completed
#             # Create a transaction record
#             Transaction.objects.create(
#                 transaction_type='CREDIT', 
#                 amount=self.amount, 
#                 # account=self.account, 
#                 # bank=self.account.bank
#                 account_from=None,
#                 account_to=self.account,
#                 bank_from=None,
#                 bank_to=self.account.bank
#             )
#             super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Deposit {self.id} - Amount: {self.amount} on {self.transaction_date}"


# class Withdraw(models.Model):
#     account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="withdrawals")
#     amount = models.DecimalField(max_digits=15, decimal_places=2)
#     transaction_date = models.DateTimeField(auto_now=True)
#     status = models.CharField(max_length=50, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], default='PENDING')
#     # user = models.ForeignKey(User, on_delete=models.CASCADE)  # Explicit user field

#     def save(self, *args, **kwargs):
#         if not self.user_id:
#             raise ValueError("User must be set for the withdrawal.")
        
#         with transaction.atomic():
#             account = self.account
#             # Ensure the user has access to the account
#             # if account.user != self.user:
#             #     raise ValueError("Account not found or you don't have access to this account.")
            
#             if account.withdraw(self.amount):  # Try withdrawing
#                 self.status = 'COMPLETED'
#                 # Create a transaction record
#                 Transaction.objects.create(
#                     transaction_type='DEBIT',
#                     amount=self.amount,
#                     account_from=self.account,
#                     account_to=None,
#                     bank_from=self.account.bank,
#                     bank_to=None
#                 )
#                 super().save(*args, **kwargs)  # Save withdrawal if successful
#             else:
#                 raise ValueError("Insufficient funds for withdrawal")  # If insufficient funds

#     def __str__(self):
#         return f"Withdraw {self.id} - Amount: {self.amount} on {self.transaction_date}"



