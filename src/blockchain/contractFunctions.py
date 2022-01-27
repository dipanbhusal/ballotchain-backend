from .contractConfig import contract

def admin():
    """
    Calls electionAdmin function from smart contract
    """
    return contract.functions.electionAdmin().call()

def state():
    """
    Calls electionState function from smart contract
    """
    return contract.functions.electionState().call()


def totalVotes():
    """
    Calls countVoteCasted function from smart contract    
    """
    return contract.functions.countVoteCasted().call()


def totalVoters():
    """
    Calls totalVoters function from smart contract    
    """
    return contract.functions.totalVoters().call()


def totalCandidates():
    """
    Calls totalCandidates function from smart contract    
    """
    return contract.functions.totalCandidates().call()


def voter(address):
    """
    Calls voter function from smart contract    
    """
    return contract.functions.voters(address).call()


def candidate(address):
    """
    Calls candidate function from smart contract    
    """
    return contract.functions.candidates(address).call()



def electionResult():
    """
    Calls electionResult function from smart contract    
    """
    return contract.functions.electionResult().call()

