import json 
import os

from .authenticate import w3
# with open('/home/dipan/project/online-voting-system-backend/src/blockchain/contract.json') as f:
with open('/Users/xxxx/dpn/7th sem/project work/online-voting-system-backend/src/blockchain/contract.json') as f:

    contract_iface = json.load(f)

contract_address = "0xD7935367885406C1F9c89d7425E00FB2E11c687f"

contract = w3.eth.contract(address=contract_address,
    abi=contract_iface['abi']
)