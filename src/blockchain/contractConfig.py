import json 
import os

from .authenticate import w3

with open('/Users/xxxx/dpn/7th sem/project work/online-voting-system-backend/src/blockchain/contract.json') as f:
    contract_iface = json.load(f)

contract_address = "0xF58E4f3dD4F45876D3aa288EbC08809533657B9A"

contract = w3.eth.contract(address=contract_address,
    abi=contract_iface['abi']
)