from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from accounts.accountOperations import _createUser
from accounts.cryptography import RSA, CryptoFernet

from .models import Candidate, Districts, Profile, Province, RSAKeys, Users
from .extraModules import getSHA256Hash, prepareKeys

rsa = RSA()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, )
    password2 = serializers.CharField(write_only=True, required=True)
    # user_type = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Users
        fields = ('first_name', 'last_name', 'email', 'citizenship_no', 'password', 'password2')
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords didn't match"})
        
        return data
    
    def create(self, validated_data):
        
        data = _createUser(validated_data)
        if data['status'] == 200:
            # sha256Hash = getSHA256Hash(validated_data['password'])
            # fernet = CryptoFernet(sha256Hash)
            # rsa_obj = RSAKeys.objects.create(user=data['user'], num_exp_d=fernet.encrypt(data['n_e_d']))
            return data['user']
        else:
            data = {
                "message": {
                    "citizenship_no": [
                        "User with given citizenship already exists."
                    ]
                },
                "details": {}
            }
            raise serializers.ValidationError(data)


class CandidateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('')

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Districts
        fields = ('name',)


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ('name',)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
    
    def to_representation(self, instance):
        return super().to_representation(instance)
