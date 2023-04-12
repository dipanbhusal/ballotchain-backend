from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render, HttpResponse
from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins, viewsets
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.accountOperations import add_to_chain

from accounts.cryptography import CryptoFernet
from accounts.middleware import get_user

from accounts.serializers import ProfileAllSerializer, ProfileSerializer, UserRegisterSerializer
from election.models import Election

from .models import Profile, Users
from .extraModules import crypOperation, getSHA256Hash, prepareKeys
# Create your views here.

class APILoginView(APIView):
    """
        API to login user
        Inputs: email, citizenship_no, password
        API Endpoint: api/accounts/login/
    """
    def dispatch(self, *args, **kwargs):
        self.payload = {
            'message':{}, 'details': {}
        }
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        citizenship_no = data.get('citizenship_no')
        password = data.get('password')
    
        user = Users.objects.filter(email=email).first()
        if user:
            if user.is_active:
                key = getSHA256Hash(password)
                fernet = CryptoFernet(key)

                citizenship_no_decrypted = fernet.decrypt(user.citizenship_no )
                if citizenship_no == citizenship_no_decrypted:
                    user_obj = authenticate(self.request, email=email, password=password )
                    if user_obj != None:
                        refresh = RefreshToken.for_user(user)
                        token = {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token)
                        }
                        user_data = {
                            'id': user.id
                        }
                        self.payload['message'] = 'User logged in successfully'
                        self.payload['details']['token'] = token

                        profile = Profile.objects.get(user=user)
                        cache.set(f"{user.id}_user", password)
                        self.payload['details']['user'] =  ProfileSerializer(profile).data
                        election = None
                        if profile.enrolled_election:
                            election = profile.enrolled_election.public_key
                        
                        self.payload['details']['enrolled_election'] = election
                        # self.payload['details']['userData'] =
                        return Response(self.payload, status=status.HTTP_200_OK)
                    else:
                        self.payload['message'] = "Incorrect password"
                else:
                    self.payload['message'] = "Incorrect citizenship number"
            else:
                self.payload['message'] = "Please verify your email to login."
        else:
            self.payload['message'] = 'Incorrect email'
        return Response(self.payload, status=status.HTTP_403_FORBIDDEN)
        # return  Response(self.payload, status=status.HTTP_400_BAD_REQUEST)


class APIRegisterView(APIView):
    """
        API to register user
        Inputs: first_name, last_name, email, citizenship_no, password, password2
        API Endpoint: api/accounts/register/
    """
    def dispatch(self, *args, **kwargs):
        self.payload = {
            'message':{}, 'details': {}
        }
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def post(self,request,  *args, **kwargs):
        data = request.data
        data._mutable = True
        print(data)
        if data.get('enrolled_election') != "":
            data['enrolled_election'] = Election.objects.get(id=data['enrolled_election']).id
        serializer = UserRegisterSerializer(data=data)
        # serializer.is_valid(raise_exception=True)

        if serializer.is_valid():
            serializer.save()
            self.payload['message'] = "User Created Successfully"
            return Response(self.payload, status=status.HTTP_200_OK, )
        self.payload['message'] = serializer.errors
        return Response(self.payload, status=status.HTTP_400_BAD_REQUEST)



class ProfileView(APIView):
    authentication_classes = (JWTAuthentication, )
    """
    API to View, Edit Profile  of user. 
    """
    def dispatch(self, *args, **kwargs):
        self.payload = {
            'message':{}, 'details': {}
        }
        return super(self.__class__, self).dispatch(*args, **kwargs)
    
    def get(self, *args, **kwargs):
        profile = Profile.objects.get(user=self.request.user)
        serializer = ProfileAllSerializer(profile)
        self.payload['message'] = 'Profile fetched successfully'
        self.payload['details']['profile'] = serializer.data
        return Response(self.payload, status=status.HTTP_200_OK)


class ProfileUpdateView(generics.UpdateAPIView):
    authentication_classes = (JWTAuthentication, )

    def dispatch(self, *args, **kwargs):
        self.payload = {
            'message':{}, 'details': {}
        }
        return super(self.__class__, self).dispatch(*args, **kwargs)
    
    def update(self, *args, **kwargs):
        data = self.request.POST
        data._mutable = True
        profile = Profile.objects.get(user=self.request.user)
        if (not profile.citizenship_image_front and  self.request.FILES.get('citizenship_image_front', None) is not None) or (profile.citizenship_image_front and self.request.FILES.get('citizenship_image_front', None) is not None) :
            data['citizenship_image_front'] = self.request.FILES.get('citizenship_image_front')
        elif profile.citizenship_image_front and  self.request.FILES.get('citizenship_image_front', None) is None:
            data['citizenship_image_front'] = profile.citizenship_image_front
        if (not profile.citizenship_image_back and  self.request.FILES.get('citizenship_image_back', None) is not None) or (profile.citizenship_image_back and self.request.FILES.get('citizenship_image_back', None) is not None) :
            data['citizenship_image_back'] = self.request.FILES.get('citizenship_image_back')
        elif profile.citizenship_image_back and  self.request.FILES.get('citizenship_image_back', None) is None:
            data['citizenship_image_back'] = profile.citizenship_image_back
        data._mutable = False
        profile = Profile.objects.get(user=self.request.user)
        serializer = ProfileAllSerializer(Profile.objects.get(user=self.request.user), data=data)
        if serializer.is_valid():
            self.perform_update(serializer)
            # if profile.enrolled_election:
            #     add_to_chain(profile)
            self.payload['message'] = 'Profile updated successfully'
            self.payload['details'] = serializer.data
            return Response(self.payload, status=status.HTTP_200_OK)

        return Response(self.payload, status=status.HTTP_400_BAD_REQUEST)





# {'baseFeePerGas': 9, 
# 'difficulty': 2, 
# 'proofOfAuthorityData': HexBytes('0x696e667572612e696f00000000000000000000000000000000000000000000003b35466daa12a56615f4fc8ed20b3e49d0c9fbb6ecc10688eaff3d1493a5fb1432893f22c488a51eab7b3785c5f0a195adf21a200f683bc0f45e7644f0cd278100'), 
# 'gasLimit': 30000000, 
# 'gasUsed': 2638471, 
# 'hash': HexBytes('0x731a579e305a163ff449ceb2fd07bb9acf4ca39412f81fa94db5bc023ce8da6e'), 
# 'logsBloom': HexBytes('0x020000803230000042802000000000002000000800000080008000060000000000000040000000021000000002000000000440000020204000001080012028210000200004000000002000084080440000210100000080020020000008000008000009018200000000000440020008000060000000000011000000100000000000010120024400000001400000100000004000000000008402000000002006000308000002040004000000080000002000000100012000800000080000000212000000021000000000408000001000000a0000200000000000000120000020000010000000300510001000010000080000002000010000010000010020000041'), 
# 'miner': '0x0000000000000000000000000000000000000000', 
# 'mixHash': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000'), 
# 'nonce': HexBytes('0x0000000000000000'), 
# 'number': 10513014, 
# 'parentHash': HexBytes('0xbf08b51d95236dde90363f2fc61a3c5a4aac2a21c088d1934b15ce8f5fb66920'), 
# 'receiptsRoot': HexBytes('0xb9a985223a4a0dde3a9455e506b7ae41ed74372d4c266261730ed21167dfbf0d'), 
# 'sha3Uncles': HexBytes('0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347'), 
# 'size': 12086, 
# 'stateRoot': HexBytes('0x914e9b3f70a2761a4d4534ac5392868e0bee2a827e59dc5236ba031bd6a0a7a1'), 
# 'timestamp': 1650093729, 
# 'totalDifficulty': 17422069, 
# 'transactions': [HexBytes('0x7ee8593ac249f46024b98d168c7eb9def33c4c1f0ac1e836f70953c2ea462990'), HexBytes('0x5c6313c374520d688a4d8387a8264ca2130b5b9fbe5f5d0a6847836c24212988'), HexBytes('0xa043c698f68c7cd5bd89a2313a82966d446084972b7e019fc4daeea471f593d5'), HexBytes('0xb4e739d62b63ed6cc37682a3bc427c87bce193ac4f058d87319368bed284a7a8'), HexBytes('0x769902d8ee9fe32b9392352f6970fc6dc43cbc0ef176c950809dcce2671e8284'), HexBytes('0xa446498fd715438b82b0f75b3e8f937a41703e6af06b8e008512e3442be9c1bd'), HexBytes('0x840381ae4d440f123bd9669c8f2331de309e68507bded11b741e958f3b9188d7'), HexBytes('0xa31aefcdf4961a71f18416347cc07ce0505efabbd6bb188d924c9e0ca5604765'), HexBytes('0x2cff84d932ef3b9bc4199e2ca183c27a8ecfc5436eacae6e65361b273c832c3f'), HexBytes('0x838da0a3bf6f30e4cd97a915464c725fe88ed71a8157321e03325891bf018784'), HexBytes('0x3035d36be0980b275ba3d459341c4d2fce2bb7b44357a4003d292ac743ec869b'), HexBytes('0xe354cb5624706631dc10c1fc4d4e7bbac20b0c80b56c02f56be523f4483b5641'), HexBytes('0xe4e66ae11cc992fbc477157b256bc453303edc154e69d396c2e671df952aa0de'), HexBytes('0x8c8a84368581f691b9fb22673b914eece52f04e918908704e9869674814838fc'), HexBytes('0x4b5a6e22b2b2f1f8ac008982894b9d7202e697066391786324937ace306fad85'), HexBytes('0x8907bc22e01b8dae1744593688198f33c69b93a915cca5b4bd15414fb1cb71e0'), HexBytes('0xfa5e559e14c3562f1935f777a134972adfa9aee8b64a8a01e50e3f4985b8234a'), HexBytes('0x30f059c062eceaab1e1c8ea804be0ad66d1a67dacc95111f5f59c1b736fc95c1'), HexBytes('0xf5a90084c2f4c7338c71080f44c86d3da84e663a0069bd1731eec57a91a2a357'), HexBytes('0xc50629cc2f932bab3f8ad315f6f50a0b8aba4acb250700fd75e2db72fddea3f4'), HexBytes('0x879982779cfc110f1ae25f732e608a8bfb0cdcece68fbce1c71652266c6b489d'), HexBytes('0xd466c92e8cec1a9c7c7f08fb944f4d10e78e9bbc1296e5ead41b0c0dd3ddb7a2'), HexBytes('0xcf46071d0a9a647b4d8831e6ed3278b091fd0912e0f1d841759db074232e74c7'), HexBytes('0xac3fc836fa9f1c77ab3202ab460642d84dec9b84d10d6d616cfa504473028dce'), HexBytes('0x7ec6b15a87aae7f4f6747d1f22c1f820c06f977925331facb03f3f8eac4540a8')], 
# 'transactionsRoot': HexBytes('0x7b2e234dbfffffee3f2a5a2ba765b0f212986f57074d13772324c2910959ac92'), 
# 'uncles': []}
