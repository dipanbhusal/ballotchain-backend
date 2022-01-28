import random
from cryptography.fernet import Fernet

PRIME_NUMBERS = [
#     1009,
# 1013,
# 1019,
# 1021,
# 1031,
# 1033,
# 1039,
1049,
1051,
1061,
1063,
1069,
1087,
1091,
1093,
1097,
1103,
1109,
1117,
1123,
1129,
1151,
1153,
1163,
1171,
1181,
1187,
1193,
# 101,
# 103,
# 107,
# 109,
# 113,
# 127,
# 131,
# 137,
# 139,
# 149,
# 151,
# 157,
# 163,
# 167,
# 173,
# 179,
# 181,
# 191,
# 193,
# 197
]

class RSA:
    def gcd(self, first, second):
        """
        Generate GCD using Euclidean algorithm
        """
        if (second == 0):
            return first
        else:
            return self.gcd(second, first % second)
    
    def egcd(self, first, second):
        """
        Extended Euclidean algorithm to return gcd, coefficient of first, second and coefeicient of second
        """

        a, old_a = 0, 1
        b, old_b = 1, 0

        while (second != 0):
            quotient = first // second
            first, second = second, first - quotient * second
            old_a, a = a, old_a - quotient * a
            old_b, b = b, old_b - quotient * b
        
        return first, old_a, old_b
    

    def chooseExp(self, totient):
        """
        Chooses random number i.e q < e < totient, and checks whether it is coprime with totient or not. 
        i.e. gcd(e, totient) = 1
        """

        while (True):
            exp = random.randrange(2, totient)

            if (self.gcd(exp, totient) == 1):
                return exp
            
    def computeNums(self):
        """
        Returns public and private keys
        """
        #Choose random prime numbers from list
        prime_num1 = PRIME_NUMBERS[random.randint(0,len(PRIME_NUMBERS)-1)]
        prime_num2 = PRIME_NUMBERS[random.randint(0,len(PRIME_NUMBERS)-1)]

        # compute n, totient and e
        n = prime_num1 * prime_num2
        totient = (prime_num1 -1) * (prime_num2 -1)
        exp = self.chooseExp(totient)

        #Compute d, 1<d<totient and ed = 1 (mod totient)
        
        gcd, a, b = self.egcd(exp, totient)

        #check if d is positive 
        if(a < 0):
            d = a + totient
        else:
            d = a
        
        num_e_d = str(n) + '-' + str(exp) + '-' + str(d)
        return num_e_d
    

    def encrypt(self, message, public_key, block_size=2):
        encrypted_blocks = []
        ciphertext = -1

        if(len(message) > 0):
            ciphertext = ord(message[0])
        
        for i in range(1, len(message)):
            if (i % block_size == 0):
                encrypted_blocks.append(ciphertext)
                ciphertext = 0
            
            ciphertext = ciphertext * 1000 + ord(message[i])
        
        encrypted_blocks.append(ciphertext)

        #encrypt all numbers by taking to power of e and modding by n
        n = public_key[0]
        e = public_key[1]
        for i in range(len(encrypted_blocks)):
            encrypted_blocks[i] = str((encrypted_blocks[i]**e) % n)
        
        encrypted_message = ' '.join(encrypted_blocks)
        return encrypted_message

    def decrypt(self, cipher, private_key, blocks_size=2):
        n = private_key[0]
        d = private_key[1]
        list_of_ciphers = cipher.split(' ')
        int_cipher = []
        for i in list_of_ciphers:
            int_cipher.append(int(i))

        message =""

        for i in range(len(int_cipher)):
            int_cipher[i] = (int_cipher[i]**d) % n
            temp = ""

            for j in range(blocks_size):
                temp = chr(int_cipher[i] % 1000) + temp
                int_cipher[i] //=1000

            message += temp
        return message


# Private:  [33389, 7771]
# Public:  [33389, 24019]
# 2131313123 ::: 19472 25752 25752 25752 6998

# print(RSA().encrypt( "dipan", [33389, 24019]))
# print(RSA().decrypt( "26269 30876 32175", [33389, 7771]))

class CryptoFernet:
    def __init__(self, key):
        self.key = key
        self.fernet=Fernet(self.key)
    
    def encrypt(self, text):
        bytes_text = bytes(text, 'utf-8')
        try:
            cipher= self.fernet.encrypt(bytes_text)
            return cipher.decode('utf-8')
        except:
            return None
    
    def decrypt(self, cipher):
        bytes_text = bytes(cipher, 'utf-8') 
        try:
            plain = self.fernet.decrypt(bytes_text).decode('utf-8')
            return plain
        except :
            return None