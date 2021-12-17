from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Create your models here.

USER_TYPES = (
    ('voter', 'voter'),
    ('admin', 'admin'),
    ('candidate', 'candidate')
)

class AuditFields(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey('Users', on_delete=models.CASCADE)


class UserManager(BaseUserManager):
    def create_user(self, contact_no, citizenship_no,  first_name, last_name, is_active=True, password=None):
        if not contact_no:
            raise ValueError('Contact Number is required')
        if not citizenship_no:
            raise ValueError('Citizenship number is requried')
        if not first_name:
            raise ValueError('First Name is required')
        if not last_name:
            raise ValueError('Last Name is required')
        
        user_obj = self.model(
            contact_no=contact_no, citizenship_no=citizenship_no, first_name=first_name, last_name=last_name, is_active=is_active
        )

        user_obj.set_password(password)    
        user_obj.save(using=self._db)
        return user_obj

    
    def create_superuser(self, contact_no, citizenship_no, first_name, last_name, password):
        user_obj = self.create_user(contact_no=contact_no, citizenship_no=citizenship_no, first_name=first_name, last_name=last_name, password=password, is_active=True)
        user_obj.is_superuser = True
        user_obj.is_staff = True
        user_obj.user_type = 'admin'
        user_obj.save(using= self._db)
        return user_obj


class Users(AbstractBaseUser, PermissionsMixin):
    contact_no = models.CharField(max_length=10, unique=True)
    citizenship_no = models.TextField()
    first_name = models.TextField()
    last_name = models.TextField()

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    is_verified = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)

    USERNAME_FIELD = 'contact_no'
    REQUIRED_FIELDS = ('citizenship_no', 'first_name', 'last_name')

    objects = UserManager()

    def __str__(self,):
        return self.first_name + ' ' + self.last_name

    class Meta:
        verbose_name_plural = 'Users'

class RSAKeys(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    public_key = models.CharField(max_length=255)
    private_key = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'RSA Keys'