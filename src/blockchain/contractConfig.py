import json 
import os

from .authenticate import w3

with open('/Users/xxxx/dpn/7th sem/project work/online-voting-system-backend/src/blockchain/contract.json') as f:
    contract_iface = json.load(f)

contract_address = "0x56eD7032d191134D64A4Ac321135AAa7cc6a4bb2"

contract = w3.eth.contract(address=contract_address,
    abi=contract_iface['abi']
)