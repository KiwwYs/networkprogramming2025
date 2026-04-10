# config.py  –  Week 8: Opportunistic Routing
# ============================================================
# Shared configuration for all nodes.
# To run multiple nodes, each node sets its own BASE_PORT.
# ============================================================

HOST = "127.0.0.1"
BASE_PORT = 9000          # Change per node: 9000, 9001, 9002, ...
PEER_PORTS = [9001, 9002] # Ports of other nodes to connect to

BUFFER_SIZE = 1024

# Opportunistic forwarding threshold:
# Only forward a message to a peer whose delivery probability >= this value.
FORWARD_THRESHOLD = 0.5

# Interval (seconds) between forwarding attempts
UPDATE_INTERVAL = 5
