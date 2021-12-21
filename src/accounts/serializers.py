from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from accounts.cryptography import RSA

from .models import RSAKeys, Users
from .extraModules import prepareKeys

rsa = RSA()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Users
        fields = ('first_name', 'last_name', 'contact_no', 'citizenship_no', 'password', 'password2')
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords didn't match"})
        
        return data
    
    def create(self, validated_data):
        
        user = Users(
            contact_no=validated_data['contact_no'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            citizenship_no=validated_data['citizenship_no']
        )
        user.set_password(validated_data['password'])
        user.save()
        
        public_key, private_key = rsa.computeNums()
        rsa_obj = RSAKeys.objects.create(user=user, public_key=public_key, private_key=private_key)
        prepared_public_key, prepared_private_key = prepareKeys(rsa_obj.public_key, rsa_obj.private_key)
        user.citizenship_no = rsa.encrypt(validated_data['citizenship_no'], prepared_public_key)
        # user.first_name = rsa.encrypt(validated_data['first_name'], prepared_public_key)
        # user.last_name = rsa.encrypt(validated_data['last_name'], prepared_public_key)
        user.save()
        return user


