from rest_framework import generics

from api.models import User
from .models import Customer, Account, Transaction
from .serializers import BankSerializer, CustomerSerializer, AccountSerializer
from rest_framework.permissions import IsAuthenticated                          
from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Account

# Existing Views (No changes)

class BankListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BankSerializer
    def get_queryset(self):
        user = self.request.user
        print(user)  
        if user.is_staff:
            return Account.objects.all()
        else:
            return Account.objects.filter(user=user)



class CustomerListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = CustomerSerializer
    def get_queryset(self):
        user = self.request.user
        print(user)  
        if user.is_staff:
            return Customer.objects.all()
        else:
            return Customer.objects.filter(user=user)


class CustomerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer

    def get_queryset(self):
        user = self.request.user
        print(user)  
        if user.is_staff:
            return Customer.objects.all()
        else:
            return Customer.objects.filter(user=user)


class AccountListCreateView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]    
    serializer_class = AccountSerializer

    def get_queryset(self):
        user = self.request.user
        print(user)  
        if user.is_staff:
            return Account.objects.all()
        else:
            return Account.objects.filter(user=user)
        

# @api_view(['POST'])
# def create_account(request):
#     # Ensure that the user field is in the request data
#     user_id = request.data.get('user')
#     if not user_id:
#         return Response({"detail": "User field is required."}, status=status.HTTP_400_BAD_REQUEST)

#     # Optionally, you can validate if the user exists in the database
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

#     # Add the user to the data to be serialized
#     data = request.data
#     data['user'] = user.id  # Make sure to pass the valid user ID

#     serializer = AccountSerializer(data=data)
#     if serializer.is_valid():
#         account = serializer.save()  # Save the account with the provided user
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]    
    serializer_class = AccountSerializer

    def get_queryset(self):
        user = self.request.user
        print(user)  
        if user.is_staff:
            return Account.objects.all()
        else:
            return Account.objects.filter(user=user)



# class DepositListCreateView(generics.ListCreateAPIView):
#     serializer_class = DepositSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Deposit.objects.filter(account__user=self.request.user)

#     def perform_create(self, serializer):
#         account_id = serializer.validated_data['account'].id
#         account = Account.objects.filter(user=self.request.user, id=account_id).first()
#         if not account:
#             raise ValidationError("Account not found or you don't have access to this account.")
#         serializer.save(account=account)


# class WithdrawListCreateView(generics.ListCreateAPIView):
#     serializer_class = WithdrawSerializer
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [JWTAuthentication]

#     def get_queryset(self):
#         return Withdraw.objects.filter(account__user=self.request.user)

#     def perform_create(self, serializer):
#         account_id = serializer.validated_data['account'].id
#         account = Account.objects.filter(user=self.request.user, id=account_id).first()
#         if not account:
#             raise ValidationError("Account not found or you don't have access to this account.")
#         serializer.save(account=account, user=self.request.user)  # Ensure user is set


    #    from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Account, Transaction
from .serializers import AccountSerializer  # Assuming you have a serializer for Account
# from .authentication import JWTAuthentication
from django.utils.timezone import now
from decimal import Decimal
from django.db import transaction as db_transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction
from .serializers import TransactionSerializer
from django.core.mail import send_mail


class TransferAPIView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    # GET Method to fetch all available accounts
    def get(self, request, *args, **kwargs):
        """
        Fetch all available accounts for selection as `account_to`.
        """
        accounts = Account.objects.all()  # Fetch all accounts
        serializer = AccountSerializer(accounts, many=True)  # Serialize account data
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            # Create the transaction
            serializer = TransactionSerializer(data=request.data)

            if not serializer.is_valid():
                return Response({
                    'data': serializer.errors,
                    'message': 'Validation failed.',
                }, status=status.HTTP_400_BAD_REQUEST)

            transaction = serializer.save()

            # Generate transaction slip content
            slip_content = (
                f"Transaction ID: {transaction.transaction_id}\n"
                f"Date: {transaction.transaction_date}\n"
                f"Type: {transaction.transaction_type}\n"
                f"From Account: {transaction.account_from.id if transaction.account_from else 'N/A'}\n"
                f"To Account: {transaction.account_to.id if transaction.account_to else 'N/A'}\n"
                f"Amount: {transaction.amount}\n"
                f"Status: {transaction.status}\n"
            )

            # Prepare the recipient emails
            recipient_emails = set()
            if transaction.account_from:
                recipient_emails.add(transaction.account_from.user.email)  # Sender's email
            if transaction.account_to:
                recipient_emails.add(transaction.account_to.user.email)  # Receiver's email

            # Send email to both accounts
            send_mail(
                subject="Transaction Receipt",
                message=slip_content,
                from_email="shaurya.joshi@openxcell.com",
                recipient_list=list(recipient_emails),
            )

            return Response({
                'message': 'Transaction completed successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'message': 'An error occurred.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
