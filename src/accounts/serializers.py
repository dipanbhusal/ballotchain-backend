from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import Users

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Users
        fields = ('first_name', 'last_name', 'contact_no', 'citizenship_no', 'password', 'password2')
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords didn't matched"})
        
        return data
    
    def create(self, validated_data):
        user = Users.objects.create(
            contact_no=validated_data['contact_no'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            citizenship_no=validated_data['citizenship_no']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user