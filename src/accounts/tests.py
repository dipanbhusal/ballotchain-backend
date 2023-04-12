import json
from django.test import TestCase
from accounts.cryptography import CryptoFernet
from accounts.extraModules import getSHA256Hash

from accounts.models import Profile, Users

# Create your tests here.

class AccountRegisterTest(TestCase):
    def setUp(self,):

        self.data = {
                "first_name": "Ram",
                "last_name": "Shrestha",
                "citizenship_no": "12345678",
                "email": "ram@gmail.com",
                "password": "ram@123", 
                "password2": "ram@123"
            }

    def test_user_register(self):
        self.data['password'] = 'anotherpwd'
        self.data['password2'] = 'anotherpwd'
        print('\n---------Testing User Registeration True--------')
        response = self.client.post('/api/accounts/register/', data=self.data)
        self.assertEqual(response.status_code, 200)
    
    def test_password_not_match(self, ):
        print('\n---------Testing User Registeration Password Not Match--------')
        self.data['password2'] = 'anotherpwd'
        # self.password_related_error_data['message']['password'][0] = "Passwords didn't match"
        response = self.client.post('/api/accounts/register/', data=self.data)
        self.assertEqual(response.status_code, 400)
    
    def test_short_password(self, ):
        print('\n---------Testing User Registeration Password Length Less Than 8--------')
        self.data['password2'] = 'ram@123'
        # self.password_related_error_data['message']['password'][0] = "Passwords must be minimum of 8 characters"
        response = self.client.post('/api/accounts/register/', data=self.data)
        self.assertEqual(response.status_code, 400)
    


class AccountLoginTest(TestCase):
    def setUp(self):
        self.credentials = {
            "first_name": "Ram",
            "last_name": "Shrestha",
            "citizenship_no": "12345678",
            "email": "ram@gmail.com",
            "password": "ram@123"
        }
        self.create_user()
    def test_user_login(self):
        print('\n---------Testing User Login True--------')
        login_data = { 
            "citizenship_no": "12345678",
            "email": "ram@gmail.com",
            "password": "ram@123"
        }
        response = self.client.post('/api/accounts/login/', data=login_data)
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['message'], "User logged in successfully")
    
    def test_incorrect_password(self,):
        print('\n---------Testing User Incorrect Password--------')
        login_data = { 
            "citizenship_no": "12345678",
            "email": "ram@gmail.com",
            "password": "ram@1234"
        }
        response = self.client.post('/api/accounts/login/', data=login_data)

        self.assertEqual(response.status_code, 403)
    

    def create_user(self, ):
        key = getSHA256Hash(self.credentials['password'])
        fernet = CryptoFernet(key)
        self.credentials["citizenship_no"] = fernet.encrypt(self.credentials['citizenship_no'])
        user = Users.objects.create_user(**self.credentials)
        user.is_active = True
        user.save()
        Profile.objects.create(user=user)