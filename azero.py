# Installation:
# pip install substrate-interface
# If this code fails to run with a bip39 (create_from_mnemonic) error, you can install within this virtual environment: "virtualenv -p python3.6 venv" and do this: "./venv/bin/pip install substrate-interface", then run with "./venv/bin/python3 azero.py"
# For other examples, see https://github.com/polkascan/py-substrate-interface
# And for interacting with SubstrateInterface, see: https://polkascan.github.io/py-substrate-interface/
# You can use this as a block explorer (transactions appear with a delay of ~10 minutes, but balances change instantly after a transaction): https://alephzero.subscan.io/
# Block explorer and wallet: https://azero.dev/
# Let's start!

# Import required libraries:
from substrateinterface import SubstrateInterface, Keypair
from scalecodec.type_registry import load_type_registry_file
from substrateinterface.exceptions import SubstrateRequestException

# Config:
rpc="https://rpc.azero.dev" # For connecting via websocket, wss://ws.azero.dev can be used.
custom_type_registry = load_type_registry_file("chainspec.json") # This file is in the repository.
ratio = 10**12 # Amounts will be divided by 10**12 to make it human-readable

# Connect to Azero network
substrate = SubstrateInterface(
	url=rpc,
  	ss58_format=0,
  	type_registry_preset='polkadot',
  	use_remote_preset=True,
  	type_registry=custom_type_registry
)

# Let's get the available balance of a random address:
address="5CK2GZvpmKYxJQXMQzHa2vvHLf5cibuWK4qkcCem2p9PXYx1"

# We can check if the address is valid or not:
isCorrectAddress= SubstrateInterface.is_valid_ss58_address(substrate, value=address) # returns True
print(isCorrectAddress)

bal=substrate.query(
	module='System',
	storage_function='Account',
	params=[address]
)

print('Balance of ' + address + 'is: ' + str(bal.value['data']['free']/ratio))

# Create a keypair and get the address of the keypair:
mnemonic = Keypair.generate_mnemonic() # It's to create a random mnemonic. The "from wallet" is this for sending AZERO.
keypair = Keypair.create_from_mnemonic(mnemonic)
created_address=keypair.ss58_address
print('Created this address: ' + created_address + ' from this newly created mnemonic: ' + mnemonic)

# Send from an address "created_address" to the "to_address" (it will fail because we have just created the address, we don't have any balance):
to_address="5CtNjnTXdMXJ4J9axyTzwYVCsxq8Cr4FN9Tb9ZZeXoVQai71" # Don't forget to change this if you're really going to send something - then don't ask me for refunds! :)
amount = 1 # Amount in AZERO

call = substrate.compose_call(
	call_module='Balances',
	call_function='transfer',
	call_params={
		'dest': to_address,
		'value': amount * ratio # sending 1 AZERO
    }
)

feeEstimation = substrate.get_payment_info(call=call, keypair=Keypair.create_from_mnemonic(mnemonic))['partialFee'] # This is to estimate the fee of the previously defined block.
# If you want to send the amount by substracting the estimated fee, you can define the block again like this:
# 'value': (1 * amount) - feeEstimation
extrinsic = substrate.create_signed_extrinsic(call=call, keypair=Keypair.create_from_mnemonic(mnemonic)) # Sends "amount" from the address of the "mnemonic" to the "to_address".
try:
	receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=False) # if you want to wait for your transaction to be included in a block, connect via websocket and make it True.
    # See: https://github.com/polkascan/py-substrate-interface#create-and-send-signed-extrinsics
	print("Extrinsic '{}' sent".format(receipt.extrinsic_hash))
except SubstrateRequestException as e:
	print("Failed to send, error message: {}".format(e))