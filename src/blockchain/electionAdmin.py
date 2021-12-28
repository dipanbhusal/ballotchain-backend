from core import settings
from .authenticate import w3
from .contractConfig import contract

credentials = settings.credentials
private_key = credentials['HOST_PRIVATE_KEY']

class ElectionAdmin:
    """
    Class for admin operation.
    """
    def __init__(self,):
        self.w3 = w3
        self.contract = contract
        self.private_key = private_key
        self.account = w3.eth.account.privateKeyToAccount(self.private_key)

    def add_voter(self, address):
        """
        Adds voter with given address to blockchain(eth) network.
        Returns recipt of transaction
        """
        init_txn = self.contract.functions\
            .addVoter(address).buildTransaction({
                'from': self.account.address,
                'nonce': self.w3.eth.getTransactionCount(self.account.address),
                'gas': 1000000,
                'gasPrice': self.w3.eth.gasPrice
            })

        signed = self.account.signTransaction(init_txn)
        txn_hash = self.w3.eth.sendRawTransaction(signed.rawTransaction)
        receipt = self.w3.eth.waitForTransactionReceipt(txn_hash)

        return dict(receipt)

    def add_candidate(self, address):
        """
        Adds voter with given address to blockchain(eth) network.
        Returns recipt of transaction
        """
        init_txn = self.contract.functions\
            .addCandidate(address).buildTransaction({
                'from': self.account.address,
                'nonce': self.w3.eth.getTransactionCount(self.account.address),
                'gas': 1000000,
                'gasPrice': self.w3.eth.gasPrice
            })

        signed = self.account.signTransaction(init_txn)
        txn_hash = self.w3.eth.sendRawTransaction(signed.rawTransaction)
        receipt = self.w3.eth.waitForTransactionReceipt(txn_hash)

        return dict(receipt)