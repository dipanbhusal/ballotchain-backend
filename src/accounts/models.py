import os
import uuid
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from election.models import Election

# Create your models here.


def citizenship_image(self, filename):
    extenstion = os.path.splitext(filename)[1].lower()
    return f'CitizenshipImage/{self.user.first_name}{extenstion}'

def party_image(self, filename):
    extenstion = os.path.splitext(filename)[1].lower()
    return f'PartyImage/{self.name}{extenstion}'


USER_TYPES = (
    ('voter', 'voter'),
    ('admin', 'admin'),
    ('candidate', 'candidate')
)

class AuditFields(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey('Users', on_delete=models.CASCADE)


class UserManager(BaseUserManager):
    def create_user(self, email, citizenship_no,  first_name, last_name, is_active=True, password=None):
        if not email:
            raise ValueError('Contact Number is required')
        if not citizenship_no:
            raise ValueError('Citizenship number is requried')
        if not first_name:
            raise ValueError('First Name is required')
        if not last_name:
            raise ValueError('Last Name is required')
        
        user_obj = self.model(
            email=email, citizenship_no=citizenship_no, first_name=first_name, last_name=last_name, is_active=is_active
        )

        user_obj.set_password(password)    
        user_obj.save(using=self._db)
        return user_obj

    
    def create_superuser(self, email, citizenship_no, first_name, last_name, password):
        user_obj = self.create_user(email=email, citizenship_no=citizenship_no, first_name=first_name, last_name=last_name, password=password, is_active=True)
        user_obj.is_superuser = True
        user_obj.is_staff = True
        user_obj.user_type = 'admin'
        user_obj.save(using= self._db)
        return user_obj


class Users(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=256, unique=True)
    citizenship_no = models.TextField()
    first_name = models.TextField()
    last_name = models.TextField()

    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    is_verified = models.BooleanField(default=False)
    # user_type = models.CharField(max_length=10, choices=USER_TYPES)

    public_name = models.CharField(max_length=100, null=True)
    citizenship_hash = models.CharField(max_length=255, null=True)

    enrolled_election = models.ForeignKey(Election, null=True, on_delete=models.SET_NULL)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('citizenship_no', 'first_name', 'last_name')

    objects = UserManager()

    def __str__(self,):
        return self.email 

    class Meta:
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):
        if not self.public_name:
            self.public_name=self.first_name + ' ' +  self.last_name
        super(self.__class__, self).save(*args, **kwargs)


# class Province(models.Model):
#     name = models.CharField(max_length=50)

#     class Meta:
#         verbose_name_plural = "Provinces"

#     def __str__(self):
#         return self.name


# class Districts(models.Model):
#     province = models.ForeignKey(Province, on_delete=models.CASCADE)
#     name = models.CharField(max_length=50)

#     def __str__(self):
#         return self.name


class Profile(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)

    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='profile')
    father_name = models.CharField(max_length=100, null=True)
    gender = models.CharField(max_length=10, choices=(('male', 'male'), ('female', 'female')), null=True)


    public_key = models.CharField(max_length=60, null=True, blank=True)
    private_key = models.CharField(max_length=255, null=True, blank=True)
    
    date_of_birth = models.DateField( null=True)
    citizenship_image_front= models.ImageField(upload_to=citizenship_image, null=True)
    citizenship_image_back= models.ImageField(upload_to=citizenship_image, null=True)

    # citizenship_issued_district = models.ForeignKey(Districts, on_delete=models.SET_NULL, null=True)

    date_submitted = models.DateTimeField(default=timezone.now)
    date_edited = models.DateTimeField(auto_now=True)
    is_voter = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    has_voted = models.BooleanField(default=False)

    district = models.CharField(max_length=255, null=True)
    provience = models.CharField(max_length=255, null=True)
    # district = models.ForeignKey(Districts, related_name="user_district", on_delete=models.SET_NULL, null=True)
    # provience = models.ForeignKey(Province, related_name="user_provience", on_delete=models.SET_NULL, null=True)
    municipality = models.CharField(max_length=50, null=True)
    ward_no = models.IntegerField('ward number', null=True)

    enrolled_election = models.ForeignKey(Election, related_name='user_enrolled_election',on_delete=models.SET_NULL, null=True)
    added_to_chain = models.BooleanField(default=False)



class Party(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name= models.CharField('party name', max_length=50)
    description = models.TextField('party description')
    logo = models.ImageField(upload_to=party_image, null=True, blank=True)
    plans = models.TextField(null=True, blank=True)
    vote_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name_plural='parties'

    def __str__(self):
        return self.name
    

class Candidate(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    bio = models.TextField('candidate\'s bio')
    plans = models.TextField('candidate\'s plan')
    added_to_chain = models.BooleanField(default=False)
    public_key = models.CharField(max_length=60, null=True, blank=True)

    vote_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    enrolled_election = models.ForeignKey(Election, related_name='candidate_enrolled_election',on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

