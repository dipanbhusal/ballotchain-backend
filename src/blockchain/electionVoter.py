from core import settings
from .authenticate import w3
from .contractConfig import contract

credentials = settings.credentials
private_key = credentials['HOST_PRIVATE_KEY']

class Voter:
    """
    Class for voter.
    modules: castVote(address)
    """
    def __init__(self, private_key):
        self.w3 = w3
        self.contract = contract
        self.private_key = private_key
        self.account = w3.eth.account.privateKeyToAccount(self.private_key)
    
    def castVote(self, candidateAddress):
        """
        Cast vote by voter to candidate address
        """
        init_txn = self.contract.functions\
            .castVote(candidateAddress).buildTransaction({
                'from': self.account.address, 
                'nonce': self.w3.eth.getTransactionCount(self.account.address),
                'gas': 1000000,
                'gasPrice': self.w3.eth.gasPrice
            })
        signed = self.account.signTransaction(init_txn)
        txn_hash = self.w3.eth.sendRawTransaction(signed.rawTransaction)
        recipt = self.w3.eth.waitForTransactionReceipt(txn_hash)

        return dict(recipt)