# config.py  –  Week 9: Bio-Inspired Networking
# ============================================================

HOST = "127.0.0.1"
BASE_PORT = 10000
PEER_PORTS = [10001, 10002]  # Example peers

BUFFER_SIZE = 1024

INITIAL_PHEROMONE = 1.0   # Starting pheromone value for each peer
DECAY_FACTOR      = 0.9   # Multiply all pheromones by this each cycle
REINFORCEMENT     = 0.1   # Amount added on successful delivery
FORWARD_THRESHOLD = 0.2   # Only forward to peers with pheromone >= this

UPDATE_INTERVAL = 5       # seconds between decay + forward attempts
