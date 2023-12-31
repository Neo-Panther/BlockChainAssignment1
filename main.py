import time
from blockchain import *
import cv2
import pprint

def getInt(prompt: str) -> int:
  while(True):
    try:
      i = int(input(prompt))
      break
    except ValueError:
      print("Input not an integer, please enter again")
  return i

def getIntArr(prompt: str) -> list[int]:
  while(True):
    try:
      inp = map(int, input(prompt).split())
      break
    except ValueError:
      print("Input not a space-separeated integer array, please enter again")
  return list(inp)

print("Creating Blockchain")
stock = {1, 2, 3}
print("Initial products with manufacturer:", stock)
manufacturer = Node(100000000, 9999, stock, NodeType.MANUFACTURER)
print("Manufacturer Node successfully created")
print("Node public info broadcasted to all nodes:") 
pprint.pp(manufacturer.getInfo())
bc = Blockchain(manufacturer)
print("Blockchain Created")
address = 9992

######  Initializing some data for demo  ######
# 7 nodes (including manufacturer) added in advance with some stock
bc.addNode(9998, 100, 'distributor', {7, 33})
bc.addNode(9997, 120, 'client', {12, 9})
bc.addNode(9996, 300, 'distributor', {660,})
bc.addNode(9995, 800, 'distributor', {80, 90})
bc.addNode(9994, 50, 'client', {70, 20})
bc.addNode(9993, 1000, 'client', {30, 40})
# 3 accepted transations (1 unverified and 2 in blocks) added in advance
t1 = Transaction(
  9999, {9,}, 9998, 9997, current_active_nodes[9998].sign(9^9998^9997)
)
t1.receiver_sign = current_active_nodes[9997].sign(9^9998^9997)
t2 = Transaction(
  9999, {90,}, 9996, 9995, current_active_nodes[9996].sign(90^9996^9995)
)
t2.receiver_sign = current_active_nodes[9995].sign(90^9996^9995)
t3 = Transaction(
  9999, {70, 20}, 9994, 9993, current_active_nodes[9994].sign(70^20^9994^9993)
)
t3.receiver_sign = current_active_nodes[9993].sign(70^20^9994^9993)
# two blocks (1 transaction each) added in advance
b1 = Block(bc.newest_block, 1, [t1, ], 9999)
bc.blockchain[b1.header_hash] = b1
b2 = Block(b1.header_hash, 2, [t2, ], 9998)
bc.blockchain[b2.header_hash] = b2
bc.newest_block = b2.header_hash
# changing state of blockchain to show the last unverified transaction
bc.accepted_transactions.append(t3)
bc.blocked_nodes.add(9994)
bc.blocked_nodes.add(9993)

wait = 3
# Main thread loop
while(True):
  for i in range(wait, -1, -1):
    print("\rMoving ahead in", i, end = '\r')
    time.sleep(1)
  print('-'*100, end = '\n\n')

  print("Current Node: ", bc.parent_node.type.name, bc.parent_node.id)
  # A Transaction can only be started or accepted if a node is unblocked
  b = 'BLOCKED' if bc.parent_node.id in bc.blocked_nodes else 'UNBLOCKED'
  print("Transaction Status: ", b)
  if b == 'BLOCKED':
    t = 'Transaction Accepted: Waiting for Validation (Mining)'
    
    for rid in bc.pending_transactions:
      for txn in bc.pending_transactions[rid]:
        if txn.sender_id == bc.parent_node.id:
          t = 'Transaction Request Sent: Waiting for Receiver id: ' + str(txn.receiver_id) + '\'s Response'
    print(t)
  print("::::::::Option Menu::::::::")
  print("To Add Node: 1")
  print("Change Current Node: 2")
  print("Start a Transaction: 3")
  print("Get Product Status: 4")
  print("Display blockchain: 5")
  print("Mine Block: 6")
  print("Display Info of Nodes, Available with Current Node: 7")
  print("Display Transaction Requests (", len(bc.pending_transactions[bc.parent_node.id]), "pending): 8")
  print("Confirm a Transaction Request: 9")
  print("Reject a Transaction Request: 10")
  print("End Connection with Blockchain: 11")
  if bc.parent_node.id == bc.manufacturer_id:
    print("Add product to Blockchain (Manufacturer's stock): 12")
  print("Delete Started Transaction: 13")
  selection = getInt("Chooose an Operation to Perform: ")
  print()
  if   selection == 1:
    n_type = input('Enter Node Type (d for distributor or c for client): ')
    while n_type not in ('c', 'd'):
      print("Invalid Node Type, please enter again")
      n_type = input('Enter Node Type (d for distributor or c for client): ')
    if n_type == 'd': n_type = 'distributor'
    else: n_type = 'client'
    stock = set(getIntArr("Enter Space Separated Unique Product-ids (leave blank to start with empty stock; repeated ids will be considered only once): "))
    inuse = stock.intersection(bc.product_locations.keys())
    while inuse:
      print("Product ids", inuse, "already in use, please enter unique ids")
      stock = set(getIntArr("Enter Space Separated unique Product-ids (leave blank to start with empty stock; repeated ids will be considered only once): "))
      inuse = stock.intersection(bc.product_locations.keys())
    
    stake = getInt("Enter Initial Security Deposit Value: ")

    bc.addNode(address, stake, n_type, stock)
    print("Node successfully created")
    print("Node public info broadcasted to all nodes:")
    pprint.pp(current_active_nodes[address].getInfo())
    wait = 3
    address -= 1
 
  elif selection == 2:
    id = getInt("Enter the Node id to Change to (Enter 0 or an Invalid id to Stop): ")
    if id not in current_active_nodes:
      print("id not Found on the Network, Stopping")
      continue
    bc.changeParentNode(id)
    wait = 1

  elif selection == 3:
    receiver_id = getInt("Enter the Receiver's id: ")
    if receiver_id not in current_active_nodes:
      print("id not Found on the Network, Stopping")
      continue
    print("Your current stock:", bc.parent_node.stock)
    product_ids = set(getIntArr("Enter Space Separated Product-ids to send, enter nothing or invalid id to stop (repeated ids will be considered only once): "))
    if not product_ids: continue
    if product_ids.difference(bc.parent_node.stock):
      print("Products not in Stock, Stopping")
      continue
    bc.startTransaction(receiver_id, product_ids)
    wait = 3

  elif selection == 4:
    product_id = getInt("Enter the product id: ")
    file_name = bc.getProductStatus(product_id)
    print("Press any key to close qr code window and continue execution::")
    # Read qr_code
    img = cv2.imread(file_name)
    
    # Output qr code with window name as 'Product_Status'
    cv2.imshow('Product ' + str(product_id) + ' Status', img)
    
    # Maintain output window until
    # user presses a key
    cv2.waitKey(0)       
    
    # Destroying present windows on screen
    cv2.destroyAllWindows()
    print("Product status saved as qr in file: ", file_name)
    wait = 2

  elif selection == 5:
    bc.showBlockchain()
    wait = 5

  elif selection == 6:
    bc.mineBlock()
    wait = 5

  elif selection == 7:
    print("Parent Node Info (with private key)::")
    print(bc.parent_node)
    print("\nOther Nodes' data available with parent (id, info)::")
    for i in bc.nodes.values():
      pprint.pp(i)
    wait = 5

  elif selection == 8:
    print(bc.getPendingTransactions())
    wait = 3
  
  elif selection == 9:
    sender_id = getInt("Enter the id of the sender of the transaction: ")
    bc.acceptTransactionRequest(sender_id)
    wait = 3
  
  elif selection == 10:
    sender_id = getInt("Enter the id of the sender of the transaction: ")
    bc.rejectTransactionRequest(sender_id)
    wait = 1

  elif selection == 11:
    print("Closing connection to the Blockchain Network...")
    break

  elif selection == 12 and bc.parent_node.id == bc.manufacturer_id:
    print("Products currently in the blockchain:", bc.product_locations.keys())
    product_ids = set(getIntArr("Enter Space Separated Unique Product-ids, enter nothing or used id to stop (repeated ids will be considered only once): "))
    if not product_ids: continue
    if product_ids.intersection(bc.product_locations.keys()):
      print("Products not in Stock, Stopping")
      continue
    bc.startTransaction(bc.manufacturer_id, product_ids)
    wait = 1
  
  elif selection == 13:
    bc.deleteTransactionRequest()
    wait = 1

  else:
    print("Incorrect input; please choose again")
    wait = 2
  