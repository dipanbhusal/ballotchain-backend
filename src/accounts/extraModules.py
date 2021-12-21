from hashlib import sha256
import base64

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
