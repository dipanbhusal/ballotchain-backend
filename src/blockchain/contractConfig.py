import json 
import os

from .authenticate import w3

with open('/Users/xxxx/dpn/7th sem/project work/online-voting-system-backend/src/blockchain/contract.json') as f:
    contract_iface = json.load(f)

contract_address = "0x8beD8DAbd3775441003232E4BBDE2B21c9884efD"

contract = w3.eth.contract(address=contract_address,
    abi=contract_iface['abi']
)