
from django.contrib import admin
from .models import Bank, Customer, Account, Transaction

# Register the Bank model
@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'location')
    search_fields = ('bank_name',)

# Register the Customer model
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'contact_info', 'address')
    search_fields = ('user__username', 'user__email')  # Improved search fields
    list_filter = ('user__is_active',)  # Optionally filter by active status of the user

# Register the Account model
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_type', 'balance', 'customer')
    search_fields = ('id', 'account_type', 'customer__user__username')  # Improved customer search field
    list_filter = ('account_type',)

# Register the Transaction model
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'account_from', 'account_to', 'amount', 'transaction_date')
    search_fields = ('account_from__id', 'account_to__id', 'transaction_type')  # Correct search fields
    list_filter = ('transaction_type',)

# # Register the Deposit model
# @admin.register(Deposit)
# class DepositAdmin(admin.ModelAdmin):
#     list_display = ('account', 'amount', 'transaction_date', 'status')
#     search_fields = ('account__id', 'status')
#     list_filter = ('status',)

# # Register the Withdraw model
# @admin.register(Withdraw)
# class WithdrawAdmin(admin.ModelAdmin):
#     list_display = ('account', 'amount', 'transaction_date', 'status')
#     search_fields = ('account__id', 'status')
#     list_filter = ('status',)


