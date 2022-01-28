import json 
import os

from .authenticate import w3

with open('/Users/xxxx/dpn/7th sem/project work/online-voting-system-backend/src/blockchain/contract.json') as f:
    contract_iface = json.load(f)

contract_address = "0x5aE08F85e970f3b63dE8889dA7979CE19e5f37c0"

contract = w3.eth.contract(address=contract_address,
    abi=contract_iface['abi']
)