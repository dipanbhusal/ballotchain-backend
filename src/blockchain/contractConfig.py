import json 
import os

from .authenticate import w3
# with open('/home/dipan/project/online-voting-system-backend/src/blockchain/contract.json') as f:
with open('/Users/xxxx/dpn/7th sem/project work/online-voting-system-backend/src/blockchain/contract.json') as f:

    contract_iface = json.load(f)

contract_address = "0xabDb6397D1ef9b60122C67D30990DD5f7cF0682C"

contract = w3.eth.contract(address=contract_address,
    abi=contract_iface['abi']
)