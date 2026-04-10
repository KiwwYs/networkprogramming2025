# config.py  –  Week 10: Quantum-Inspired Networking
# ============================================================

HOST = "127.0.0.1"
BASE_PORT = 11000
PEER_PORTS = [11001, 11002]  # Example peers

BUFFER_SIZE = 1024

TOKEN_EXPIRY    = 10   # seconds until an unread token becomes invalid
UPDATE_INTERVAL = 5    # seconds between forwarding attempts
