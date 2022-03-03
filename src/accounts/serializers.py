from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from accounts.accountOperations import _createUser
from election.models import Election
from election.serializers import ElectionSerializer

from .models import Profile, Users



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
        if len(data['password']) < 8:
            raise serializers.ValidationError({"password": "Passwords must be minimum of 8 characters"})
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

# class DistrictSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Districts
#         fields = ('name',)


# class ProvinceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Province
#         fields = ('name',)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('is_verified', 'has_voted', 'public_key' )

class ProfileAllSerializer(serializers.ModelSerializer):
    # father_name = serializers.CharField()
    # citizenship_image_front = serializers.FileField()
    # citizenship_image_back = serializers.FileField()
    # gender = serializers.CharField()
    # provience = serializers.CharField()
    # district = serializers.CharField()
    # ward_no = serializers.IntegerField()
    # municipality = serializers.IntegerField()
    # enrolled_election = serializers.IntegerField()

    class Meta:
        model = Profile
        fields = ( 'id', 'user', 'public_key',  'father_name', 'citizenship_image_front', 'citizenship_image_back', 'date_of_birth', 'gender', 'provience', 'district', 'ward_no', 'municipality', 'enrolled_election', 'is_verified' )
    

    def to_internal_value(self, data):
        data._mutable = True
        if data.get('father_name') == 'null':
            data['father_name'] = None
        if data.get('district') == 'null':
            data['district'] = None
        if data.get('provience') == 'null':
            data['provience'] = None
        if data.get('municipality') == 'null':
            data['municipality'] = None
        if data.get('enrolled_election') == 'null':
            data['enrolled_election'] = None
        if data.get('ward_no') == 'null':
            data['ward_no'] = None
        if data.get('gender') == 'null':
            data['gender'] = None
        if data.get('date_of_birth') == 'null':
            data['date_of_birth'] = None

        return super(ProfileAllSerializer, self).to_internal_value(data)


    def update(self, instance, validated_data):
        instance.father_name = validated_data['father_name']
        instance.father_name = validated_data['father_name']

        instance.gender = validated_data['gender']
        instance.provience = validated_data['provience']
        instance.district = validated_data['district']
        instance.ward_no = validated_data['ward_no']
        instance.municipality = validated_data['municipality']
        instance.enrolled_election = validated_data['enrolled_election']
        # print(validated_data)
        # if validated_data['citizenship_image_front'] is not None:
        #     print("front1")
        instance.citizenship_image_front = validated_data['citizenship_image_front']
        # if validated_data['citizenship_image_back'] is not None:
        #     print("back1")
        instance.citizenship_image_back = validated_data['citizenship_image_back']
        # instance.save()
        return super().update(instance, validated_data)


#     def to_representation(self, instance):
#         self.
#         return super().to_representation(instance)


# class EnrolledElection(serializers.ModelSerializer):
#     class Meta:
#         model = Election
#         fields = ('title',)
    # def save(self, **kwargs):
    #     profile = Profile.objects.filter(id=self.fields['id'])
    #     profile.update(**kwargs)
    #     return profile
