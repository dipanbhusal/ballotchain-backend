from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from accounts.cryptography import CryptoFernet
from accounts.extraModules import getSHA256Hash
from accounts.models import Candidate
from blockchain.authenticate import create_account
from blockchain.electionAdmin import ElectionAdmin
from election.models import Election



def blockchain_handler(sender, instance, created, **kwargs):
    print(sender.__name__)
    if sender.__name__ == "Election":
        if created:
            account = create_account()
            instance.public_key = account.address
            # print('id::',instance.password)
            # key = instance.password
            # fernet = CryptoFernet(getSHA256Hash(key))
            # cipher_private_key = fernet.encrypt(account.privateKey.hex())
            # instance.private_key =  cipher_private_key
            admin = ElectionAdmin()
            recipt = admin.add_election(instance.public_key)
            txn_hash = recipt['transactionHash'].hex()
            url = f'https://rinkeby.etherscan.io/tx/{txn_hash}'
            if recipt['status']:
                instance.added_to_chain = True
            instance.save()

    elif sender.__name__ == "Candidate":
            
        if created:
            account = create_account()
            instance.public_key = account.address
            # print('id::',instance.password)
            # key = instance.password
            # fernet = CryptoFernet(getSHA256Hash(key))
            # cipher_private_key = fernet.encrypt(account.privateKey.hex())
            # instance.private_key =  cipher_private_key
            admin = ElectionAdmin()
            recipt = admin.add_candidate(instance.public_key, instance.enrolled_election.public_key)
            txn_hash = recipt['transactionHash'].hex()
            url = f'https://rinkeby.etherscan.io/tx/{txn_hash}'
            if recipt['status']:
                instance.added_to_chain = True
            instance.save()


post_save.connect(blockchain_handler, sender=Candidate)
post_save.connect(blockchain_handler, sender=Election)