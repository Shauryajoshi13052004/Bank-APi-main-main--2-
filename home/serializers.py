from rest_framework import serializers
from api.models import User
from .models import Bank, Customer, Account, Transaction


from rest_framework import serializers
from .models import Transaction, Account

from rest_framework import serializers
from .models import Transaction, Account
from rest_framework import serializers
from .models import Transaction, Account

class TransactionSerializer(serializers.ModelSerializer):
    transaction_id = serializers.UUIDField(read_only=True)
    transaction_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    transaction_type = serializers.CharField(max_length=10)
    account_from = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False)
    account_to = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    status = serializers.CharField(max_length=20, default="pending", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'transaction_id',
            'transaction_date',
            'transaction_type',
            'account_from',
            'account_to',
            'amount',
            'status',
        ]
        read_only_fields = ['transaction_id', 'transaction_date', 'status']

    def validate(self, data):
        transaction_type = data['transaction_type']
        amount = data['amount']

        # Check conditions based on transaction type
        if transaction_type == 'TRANSFER':
            if not data.get('account_from') or not data.get('account_to'):
                raise serializers.ValidationError('Both account_from and account_to are required for a transfer.')
            if data['account_from'] == data['account_to']:
                raise serializers.ValidationError('Cannot transfer to the same account.')
            if data['account_from'].balance < amount:
                raise serializers.ValidationError('Insufficient funds for transfer.')

        elif transaction_type == 'WITHDRAWAL':
            if not data.get('account_from'):
                raise serializers.ValidationError('account_from is required for withdrawal.')
            if data['account_from'].balance < amount:
                raise serializers.ValidationError('Insufficient funds for withdrawal.')

        elif transaction_type == 'DEPOSIT':
            if not data.get('account_to'):
                raise serializers.ValidationError('account_to is required for deposit.')

        return data

    def create(self, validated_data):
        transaction_type = validated_data['transaction_type']
        account_from = validated_data.get('account_from')
        account_to = validated_data.get('account_to')
        amount = validated_data['amount']

        # Handle different transaction types
        if transaction_type == 'TRANSFER':
            if account_from and account_to:
                # Deduct from account_from and add to account_to
                account_from.balance -= amount
                account_to.balance += amount
                account_from.save()
                account_to.save()

        elif transaction_type == 'WITHDRAWAL':
            if account_from:
                # Deduct from account_from
                account_from.balance -= amount
                account_from.save()

        elif transaction_type == 'DEPOSIT':
            if account_to:
                # Add to account_to
                account_to.balance += amount
                account_to.save()

        # Create the transaction record
        transaction = Transaction.objects.create(**validated_data)
        return transaction


class AccountSerializer(serializers.ModelSerializer):
    transactions_from = TransactionSerializer(many=True, read_only=True)
    transactions_to = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'account_type', 'balance', 'transactions_from', 'transactions_to']


class CustomerSerializer(serializers.ModelSerializer):
    # Include customer_name as the user's username, or whatever field you prefer from the User model
    customer_name = serializers.CharField(source='user.email')  # Assuming 'user' is related to User model
    class Meta:
        model = Customer
        fields = ['id', 'customer_name', 'contact_info', 'address','user', 'accounts']
        depth = 1


class BankSerializer(serializers.ModelSerializer):
    accounts = AccountSerializer(many=True, read_only=True)  # Use the related_name 'accounts'
    transactions = TransactionSerializer(many=True, read_only=True)  # Use the related_name 'transactions'
    class Meta:
        model = Bank
        fields = ['id', 'bank_name', 'location', 'accounts', 'transactions']



# class DepositSerializer(serializers.ModelSerializer):
#     account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False)  # Make account optional
#     amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)  # Make amount required
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)  # Include user field if needed
#     class Meta:
#         model = Deposit
#         fields = ['id', 'account', 'amount', 'transaction_date', 'status', 'user']
# class WithdrawSerializer(serializers.ModelSerializer):
#     account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=True)  # Make account required
#     amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)  # Make amount required
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)  # Include user field if needed
#     class Meta:
#         model = Withdraw
#         fields = ['id', 'account', 'amount', 'transaction_date', 'status', 'user']
