import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class UserManager(BaseUserManager):

    def create_user(
        self,
        first_name,
        last_name,
        username,
        email,
        phone_number=None,
        password=None,
    ):
        if not email:
            raise ValueError('User must have email address...!')

        if not username:
            raise ValueError('User must have username...!')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, phone_number=None, password=None, **extra_args):
        user = self.create_user(
            email=self.normalize_email(email),
            usernam=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            phone_number=phone_number,
        )
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()

    id = models.UUIDField('ID', primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(
        _('username'),
        max_length=50,
        unique=True,
        help_text=
        _('Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.'
          ),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15, null=False, blank=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone_number']

    objects = UserManager()

    class Meta:
        managed = True
        db_table = 'es_users'

    def __str__(self):
        return str(self.id)
