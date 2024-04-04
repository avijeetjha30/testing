from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from core.account.models import User
from core.helper.utils import validate_name


class UserRegistrationSerializers(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, validators=validate_name())
    last_name = serializers.CharField(required=True, validators=validate_name())
    confirm_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'phone_number', 'password', 'confirm_password')

    def validate(self, validated_data):
        data = super().validate(validated_data)
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Password doesn't match...!")
        data['password'] = make_password(data['password'])
        data.pop('confirm_password')
        return data


class UserLoginSerializers(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, validated_data):
        data = super().validate(validated_data)
        user = User.objects.filter(email=data['email']).first()
        if not user:
            raise serializers.ValidationError('Invalid credential...!')
        if not user.is_active:
            raise serializers.ValidationError('You have to activate your account first check your email...!')
        if not check_password(data['password'], user.password):
            raise serializers.ValidationError('You enter wrong password...!')
        return data


class ActivateAccountSerializrs(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('is_active',)

    def validate(self, validated_data):
        data = super().validate(validated_data)
        encoded_pk = self.context.get('kwargs').get('encoded_pk')
        token = self.context.get('kwargs').get('token')
        pk = force_str(urlsafe_base64_decode(encoded_pk))
        user = User.objects.get(pk=pk)
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError('The activation link is invalid...!')
        User.objects.filter(pk=pk).update(is_active=True)
        return data


class RestPasswordSerializers(serializers.ModelSerializer):
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('new_password', 'confirm_password')

    def validate(self, validated_data):
        data = super().validate(validated_data)
        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError("Password doesn't match...!")
        data['new_password'] = make_password(data.get('new_password'))
        return data


class VerifyMailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, validated_data):
        data = super().validate(validated_data)
        if not User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError('Register first...!')
        return data


class ResetPasswordEmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('password',)

    def validate(self, validate_data):
        data = super().validate(validate_data)
        encoded_pk = self.context.get('kwargs').get('encoded_pk')
        token = self.context.get('kwargs').get('token')
        pk = force_str(urlsafe_base64_decode(encoded_pk))
        user = User.objects.get(pk=pk)
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError('The activation link is invalid...!')
        password = make_password(data.get('password'))
        User.objects.filter(pk=pk).update(password=password)
        return data
