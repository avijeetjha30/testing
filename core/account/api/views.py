from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
#########################################################
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from core.account.api.serializers import *
#########################################################
from core.account.models import User
from core.helper.generate_token import GenerateToken, redis_client
from core.helper.send_mail import SendMail
from core.helper.utils import api_response


# User registration
class UserRegistrationAV(GenericAPIView):
    serializer_class = UserRegistrationSerializers

    def post(self, request):
        serialized_data = self.serializer_class(data=request.data)
        if serialized_data.is_valid(raise_exception=True):
            user = serialized_data.save()
            token = PasswordResetTokenGenerator().make_token(user)
            current_domain = get_current_site(request)
            activation_link = reverse(
                'activate-account', kwargs={
                    'encoded_pk': urlsafe_base64_encode(force_bytes(user.id)),
                    'token': token
                }
            )
            activation_link = f'http://{current_domain}{activation_link}'
            subject = 'Activate account'
            email_template = './activate_account_link.html'
            mail_send = SendMail()
            mail_send.send_mail(user.email, subject, activation_link, email_template)
            api_response_data = {
                'data': None,
                'message': 'Your Registration is successfull Check email for account activation...!',
                'status_code': status.HTTP_200_OK,
                'success': True
            }  # noqa
        else:
            api_response_data = {
                'data': None,
                'message': serialized_data.errors,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'success': False
            }

        return Response(api_response(**api_response_data), status=api_response_data.get('status_code'))


# Activate user account after registration
class ActivateAccountAV(GenericAPIView):
    serializer_class = ActivateAccountSerializrs

    def patch(self, request, *args, **kwargs):
        serialized_data = self.serializer_class(data=request.data, context={'kwargs': kwargs})
        serialized_data.is_valid(raise_exception=True)
        api_response_data = {
            'data': None,
            'message': 'Congratulations, you are now verified...!',
            'status_code': status.HTTP_200_OK,
            'success': True
        }
        return Response(api_response(**api_response_data), status=api_response_data.get('status_code'))


# Login user
class UserLoginAV(GenericAPIView):
    serializer_class = UserLoginSerializers

    def post(self, request):
        serialized_data = self.serializer_class(data=request.data)
        if serialized_data.is_valid(raise_exception=True):
            user = User.objects.get(email=serialized_data.data.get('email'))
            token = GenerateToken()
            api_response_data = {
                'data': token.get_token(user),
                'message': 'You are are logged in...!',
                'status_code': status.HTTP_200_OK,
                'success': True
            }
        else:
            api_response_data = {
                'data': None,
                'message': serialized_data.errors,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'success': False
            }
        return Response(api_response(**api_response_data), status=api_response_data.get('status_code'))


# Logout user with blacklist refresh and access token
class UserLogoutAV(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            token = AccessToken(token)
            jti = token.payload['jti']
            redis_client.srem(f"user_{token.payload['email']}", jti)
            token = RefreshToken(request.META.get('HTTP_REFRESH_TOKEN'))
            token.blacklist()
            api_response_data = {
                'data': None,
                'message': 'you are logged out...!',
                'status_code': status.HTTP_200_OK,
                'success': True
            }
        except Exception as e:
            api_response_data = {
                'data': None,
                'message': str(e),
                'status_code': status.HTTP_404_NOT_FOUND,
                'success': False
            }
        response_data = api_response(**api_response_data)
        return Response(response_data, status=api_response_data['status_code'])


# Generate new access and refresh token by using refresh token
class CustomTokenRefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        serializer.is_valid(raise_exception=True)
        access = serializer.validated_data['access']
        token = AccessToken(access)
        user_id = token.payload['user_id']
        user = User.objects.filter(id=user_id).first()
        if user:
            token = GenerateToken()
            api_response_data = {
                'data': token.get_token(user),
                'message': 'Token generated...!',
                'status_code': status.HTTP_200_OK,
                'success': True
            }
        else:
            api_response_data = {
                'data': None,
                'message': 'Failed to generate token',
                'status_code': status.HTTP_400_BAD_REQUEST,
                'success': False
            }
        return Response(api_response(**api_response_data), status=api_response_data.get('status_code'))


# forgot password after login
class ResetPasswordAV(GenericAPIView):
    serializer_class = RestPasswordSerializers
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        serialized_data = self.serializer_class(data=request.data)
        if serialized_data.is_valid(raise_exception=True):
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            token = AccessToken(token)
            email = token.payload['email']
            User.objects.filter(email=email).update(password=serialized_data.data.get('new_password'))
            api_response_data = {
                'data': None,
                'message': 'Password reset...!',
                'status_code': status.HTTP_200_OK,
                'success': True
            }
        else:
            api_response_data = {
                'data': None,
                'message': serialized_data.errors,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'success': False
            }
        return Response(api_response(**api_response_data), status=api_response_data.get('status_code'))


# reset password using email send
class ForgotPasswordEmailAV(GenericAPIView):
    serializer_class = VerifyMailSerializer

    def post(self, request):
        serialized_data = self.serializer_class(data=request.data)
        if serialized_data.is_valid(raise_exception=True):
            user = User.objects.get(email=serialized_data.data.get('email'))
            token = PasswordResetTokenGenerator().make_token(user)
            current_domain = get_current_site(request)
            forgot_link = reverse(
                'forgot-password', kwargs={
                    'encoded_pk': urlsafe_base64_encode(force_bytes(user.id)),
                    'token': token
                }
            )
            forgot_link = f'http://{current_domain}{forgot_link}'
            subject = 'Rest Password'
            email_template = './reset_password.html'
            mail_send = SendMail()
            mail_send.send_mail(user.email, subject, forgot_link, email_template)
            api_response_data = {
                'data': None,
                'message': 'Reset password link is sent to your email...!',
                'status_code': status.HTTP_200_OK,
                'success': True
            }  # noqa
        else:
            api_response_data = {
                'data': None,
                'message': serialized_data.errors,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'success': False
            }
        return Response(api_response(**api_response_data), status=api_response_data.get('status_code'))


class RestPasswordEmailAV(GenericAPIView):
    serializer_class = ResetPasswordEmailSerializer

    def patch(self, request, *args, **kwargs):
        serialized_data = self.serializer_class(data=request.data, context={'kwargs': kwargs})
        serialized_data.is_valid(raise_exception=True)
        api_response_data = {
            'data': None,
            'message': 'Your password is set...!',
            'status_code': status.HTTP_200_OK,
            'success': True
        }
        return Response(api_response(**api_response_data), status=api_response_data.get('status_code'))
