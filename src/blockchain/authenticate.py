
from web3 import Web3
from core import settings

credentials = settings.credentials
w3 = Web3(Web3.HTTPProvider(credentials['INFURA_PROVIDER']))


def create_account():
    """
    Creates account on blockchain and returns account
    """
    account = w3.eth.account.create()
    return account


def retrieve_address(private_key):
    """
    Returns account from private key
    """
    account = w3.eth.account.privateKeyToAccount(private_key)
    return account.address