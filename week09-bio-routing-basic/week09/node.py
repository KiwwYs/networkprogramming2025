#!/usr/bin/env python3
# node.py  –  Week 9: Bio-Inspired Networking (Pheromone Routing)
# ============================================================
# Each node maintains a pheromone table and uses it to decide
# where to forward messages.
#
# Every UPDATE_INTERVAL seconds:
#   1. Decay all pheromone trails (evaporation)
#   2. Find candidates with pheromone >= FORWARD_THRESHOLD
#   3. Forward queued messages along strongest trails
#   4. Reinforce the path on success
#
# Run multiple nodes in separate terminals:
#   python node.py --port 10000
#   python node.py --port 10001
#   python node.py --port 10002
#
# Common mistakes this code addresses:
#   ✓ Pheromones decay every cycle (stale paths fade)
#   ✓ Failed sends do NOT reinforce (reinforcement logic intact)
#   ✓ Server runs in separate thread (non-blocking)
# ============================================================

import socket
import threading
import time
import argparse

from config import (HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE,
                    FORWARD_THRESHOLD, UPDATE_INTERVAL,
                    REINFORCEMENT, INITIAL_PHEROMONE)
from pheromone_table import PheromoneTable

# ------------------------------------------------------------------
# Shared state
# ------------------------------------------------------------------
pheromone_table = PheromoneTable()
message_queue: list[str] = []
queue_lock = threading.Lock()

MY_PORT: int = BASE_PORT


# ============================  Networking  ========================

def send_message(peer_port: int, message: str) -> bool:
    """
    Attempt to send *message* to *peer_port*.
    On success: reinforce that peer's pheromone trail.
    On failure: do NOT reinforce (path is not rewarded).
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(message.encode())
        s.close()
        print(f"[NODE {MY_PORT}] ✅ Sent: '{message}' → port {peer_port}")
        pheromone_table.reinforce(peer_port, REINFORCEMENT)  # Reinforce successful path
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        print(f"[NODE {MY_PORT}] ❌ Failed to send to {peer_port}")
        return False


def start_server() -> None:
    """TCP server: receive messages and add to queue."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, MY_PORT))
    server.listen(5)
    print(f"[NODE {MY_PORT}] 🔊 Listening for incoming messages...")

    while True:
        conn, addr = server.accept()
        data = conn.recv(BUFFER_SIZE).decode().strip()
        conn.close()
        if data:
            print(f"[NODE {MY_PORT}] 📥 Received: '{data}' from port {addr[1]}")
            with queue_lock:
                message_queue.append(data)


# ============================  Forwarding  ========================

def forward_loop() -> None:
    """
    Bio-inspired forwarding loop.

    Each cycle:
      1. Decay pheromones (evaporation — stale paths weaken)
      2. Get candidates above FORWARD_THRESHOLD
      3. Forward each queued message to the strongest candidate
    """
    while True:
        time.sleep(UPDATE_INTERVAL)

        # Step 1: Evaporation
        pheromone_table.decay()

        # Step 2: Find usable paths
        candidates = pheromone_table.get_best_candidates(FORWARD_THRESHOLD)

        if not candidates:
            print(f"[NODE {MY_PORT}] ⏳ No paths above threshold. "
                  f"Queue: {len(message_queue)}")
            continue

        print(f"[NODE {MY_PORT}] 🐜 Candidates: {candidates}  "
              f"Queue: {len(message_queue)} msg(s)")

        # Step 3: Forward queued messages
        with queue_lock:
            forwarded = []
            for msg in message_queue:
                for peer in candidates:
                    if send_message(peer, msg):
                        forwarded.append(msg)
                        break   # Move to next message after success
            for msg in forwarded:
                message_queue.remove(msg)


# ============================  CLI  ================================

def cli_loop() -> None:
    """
    Interactive CLI.

    Commands:
        send <port> <message>    send directly or queue on failure
        queue                    show queued messages
        pheromone                show pheromone table
        reinforce <port> <val>   manually add pheromone to a path
        decay                    manually trigger one decay cycle
        quit
    """
    print(f"\n[NODE {MY_PORT}] Ready. Type 'help' for commands.\n")

    while True:
        try:
            line = input(f"[{MY_PORT}]> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nShutting down.")
            break

        if not line:
            continue

        parts = line.split(None, 2)
        cmd   = parts[0].lower()

        if cmd in ("help", "?"):
            print("  send <port> <message>      attempt delivery or queue")
            print("  queue                      show message queue")
            print("  pheromone                  show pheromone table")
            print("  reinforce <port> <value>   add pheromone manually")
            print("  decay                      trigger one decay cycle")
            print("  quit")

        elif cmd == "send" and len(parts) >= 3:
            try:
                peer_port = int(parts[1])
                message   = parts[2]
            except ValueError:
                print("  Usage: send <port> <message>")
                continue
            if not send_message(peer_port, message):
                with queue_lock:
                    message_queue.append(message)
                print(f"  Queued. ({len(message_queue)} in queue)")

        elif cmd == "queue":
            with queue_lock:
                if message_queue:
                    for i, m in enumerate(message_queue, 1):
                        print(f"  [{i}] {m}")
                else:
                    print("  (empty)")

        elif cmd == "pheromone":
            pheromone_table.display()

        elif cmd == "reinforce" and len(parts) >= 3:
            try:
                pheromone_table.reinforce(int(parts[1]), float(parts[2]))
            except ValueError:
                print("  Usage: reinforce <port> <value>")

        elif cmd == "decay":
            pheromone_table.decay()

        elif cmd == "quit":
            break

        else:
            print("  Unknown command. Type 'help'.")


# ============================  Main  ==============================

def main() -> None:
    global MY_PORT

    parser = argparse.ArgumentParser(description="Week 9 – Bio-Inspired Routing Node")
    parser.add_argument("--port", type=int, default=BASE_PORT,
                        help=f"Port for this node (default: {BASE_PORT})")
    args = parser.parse_args()
    MY_PORT = args.port

    peer_ports = [p for p in PEER_PORTS if p != MY_PORT]

    # Start background threads
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # Initialize pheromones for known peers
    for peer in peer_ports:
        pheromone_table.reinforce(peer, INITIAL_PHEROMONE)

    # Attempt initial delivery; queue on failure
    for peer in peer_ports:
        msg = f"Hello from node {MY_PORT}"
        if not send_message(peer, msg):
            print(f"[NODE {MY_PORT}] Peer {peer} unavailable – queued")
            with queue_lock:
                message_queue.append(msg)

    cli_loop()


if __name__ == "__main__":
    main()
