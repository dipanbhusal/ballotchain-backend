import os
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Create your models here.


def citizenship_image(self, filename):
    extenstion = os.path.splitext(filename)[1].lower()
    return f'CitizenshipImage/{self.symbol}{extenstion}'


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


class UserProfile(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)


class Province(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Provinces"


class Districts(models.Model):

    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

class RSAKeys(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    num_exp_d = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'RSA Keys'

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

    def save(self, *args, **kwargs):
        self.num_exp_d = self.num_exp_d.decode('utf-8')
        super(self.__class__, self).save(*args, **kwargs)


class Profile(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    father_name = models.CharField(max_length=100)
    permanent_address = models.OneToOneField('PermanentAddress' ,on_delete=models.CASCADE)
    temporary_address = models.OneToOneField('TemporaryAddress', on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    citizenship_image= models.ImageField(upload_to=citizenship_image)


class TemporaryAddress(models.Model):
    district = models.ForeignKey(Districts, on_delete=models.SET_NULL, null=True)
    provience = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True)
    

class PermanentAddress(models.Model):
    district = models.ForeignKey(Districts, on_delete=models.SET_NULL, null=True)
    provience = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True)

