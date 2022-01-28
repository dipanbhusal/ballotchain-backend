from hashlib import sha256
import base64
from accounts import models

from accounts.cryptography import RSA, CryptoFernet

def prepareKeys(n_e_d):
    """
        Returns list of [n. e] as public key and [n, d] as private key from format 'n-e'
    """
    try:
        keys = n_e_d.split('-')
    except TypeError:
        keys = n_e_d.decode('utf-8').split('-')
    public_key = [int(keys[0]), int(keys[1])]
    private_key = [int(keys[0]), int(keys[2])]

    return public_key, private_key


def getSHA256Hash(text):
    """
    Takes plaintext as input and returns hash value
    """
    cipher=sha256(bytes(text, 'utf-8')).digest()
    cipher=base64.b64encode(cipher) # encoding sha hash in base64 required
    return cipher


def crypOperation(key, user=None, input_text=None, mode="encrypt"):
    rsa = RSA()
    fernet_key = getSHA256Hash(key)
    fernet = CryptoFernet(fernet_key)
    rsa_object = models.RSAKeys.objects.filter(user_id=user.id).first()

    if rsa_object:
        n_e_d = fernet.decrypt(rsa_object.num_exp_d) # returns 'n-e-d' 
        prepared_public_key, prepared_private_key = prepareKeys(n_e_d)
        if mode == "encrypt":
            cipher = rsa.encrypt(input_text, prepared_public_key)
            return cipher
        if mode == "decrypt":
            plain = rsa.decrypt(input_text, prepared_private_key)
            return plain