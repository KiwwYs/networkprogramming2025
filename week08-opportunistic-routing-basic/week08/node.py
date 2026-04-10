#!/usr/bin/env python3
# node.py  –  Week 8: Opportunistic Routing
# ============================================================
# Simulates a mobile node that:
#   1. Listens for incoming messages (TCP server)
#   2. Maintains delivery probabilities per peer (DeliveryTable)
#   3. Forwards queued messages opportunistically when a peer
#      with P >= FORWARD_THRESHOLD is reachable
#
# Run multiple nodes in separate terminals with different BASE_PORT:
#   Terminal 1:  python node.py           (uses BASE_PORT from config.py)
#   Terminal 2:  python node.py --port 9001
#   Terminal 3:  python node.py --port 9002
#
# Common mistakes this code addresses:
#   ✓ Delivery probabilities guide forwarding (not blind broadcast)
#   ✓ Failed deliveries go to queue (not dropped)
#   ✓ Server runs in a separate thread (non-blocking I/O)
# ============================================================

import socket
import threading
import time
import argparse

from config import HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE, FORWARD_THRESHOLD, UPDATE_INTERVAL
from delivery_table import DeliveryTable

# ------------------------------------------------------------------
# Shared state
# ------------------------------------------------------------------
delivery_table = DeliveryTable()
message_queue: list[str] = []
queue_lock = threading.Lock()

# Resolved at startup (may be overridden by --port argument)
MY_PORT: int = BASE_PORT


# ============================  Networking  ========================

def send_message(peer_port: int, message: str) -> bool:
    """
    Attempt to deliver *message* to the node at *peer_port*.
    Returns True on success, False on failure (node unreachable).
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(message.encode())
        s.close()
        print(f"[NODE {MY_PORT}] ✅ Sent: '{message}' → port {peer_port}")
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        print(f"[NODE {MY_PORT}] ❌ Could not reach port {peer_port}")
        return False


def start_server() -> None:
    """TCP server: accept incoming messages and add them to the queue."""
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
            print(f"[NODE {MY_PORT}] 📥 Received: '{data}' from {addr[1]}")
            with queue_lock:
                message_queue.append(data)


# ============================  Forwarding  ========================

def forward_loop() -> None:
    """
    Opportunistic forwarding loop.

    Every UPDATE_INTERVAL seconds:
      1. Find peers whose P >= FORWARD_THRESHOLD  (good encounters)
      2. For each queued message, try to forward to the best candidate
      3. Remove successfully forwarded messages from the queue
    """
    while True:
        time.sleep(UPDATE_INTERVAL)

        candidates = delivery_table.get_best_candidates(FORWARD_THRESHOLD)

        if not candidates:
            print(f"[NODE {MY_PORT}] ⏳ No suitable candidates (threshold={FORWARD_THRESHOLD}). "
                  f"Queue size: {len(message_queue)}")
            continue

        print(f"[NODE {MY_PORT}] 🔍 Candidates: {candidates}  Queue: {len(message_queue)} msg(s)")

        with queue_lock:
            forwarded = []
            for msg in message_queue:
                for peer in candidates:
                    if send_message(peer, msg):
                        forwarded.append(msg)
                        break   # Stop trying once successfully forwarded
            for msg in forwarded:
                message_queue.remove(msg)


# ============================  CLI  ================================

def cli_loop() -> None:
    """
    Simple interactive CLI for the running node.

    Commands:
        send <port> <message>    – send directly or queue
        queue                    – show queued messages
        table                    – show delivery probability table
        set <port> <prob>        – manually update a probability
        decay                    – apply aging to all probabilities
        quit                     – exit
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
            print("  send <port> <message>  – attempt delivery or queue")
            print("  queue                  – show message queue")
            print("  table                  – show delivery probabilities")
            print("  set <port> <prob>      – update delivery probability")
            print("  decay                  – apply probability aging")
            print("  quit                   – exit")

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
                print(f"  Message queued ({len(message_queue)} in queue)")

        elif cmd == "queue":
            with queue_lock:
                if message_queue:
                    for i, m in enumerate(message_queue, 1):
                        print(f"  [{i}] {m}")
                else:
                    print("  (queue empty)")

        elif cmd == "table":
            delivery_table.display()

        elif cmd == "set" and len(parts) >= 3:
            try:
                peer_port = int(parts[1])
                prob      = float(parts[2])
                delivery_table.update_probability(peer_port, prob)
            except ValueError:
                print("  Usage: set <port> <probability>")

        elif cmd == "decay":
            delivery_table.decay_all()

        elif cmd == "quit":
            break

        else:
            print("  Unknown command. Type 'help' for options.")


# ============================  Main  ==============================

def main() -> None:
    global MY_PORT

    parser = argparse.ArgumentParser(description="Week 8 – Opportunistic Routing Node")
    parser.add_argument("--port", type=int, default=BASE_PORT,
                        help=f"Port for this node (default: {BASE_PORT})")
    args = parser.parse_args()
    MY_PORT = args.port

    # Derive peer ports: all PEER_PORTS except our own
    peer_ports = [p for p in PEER_PORTS if p != MY_PORT]

    # Start background threads
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # Initialise delivery probabilities for known peers
    # In a real system these would come from encounter history.
    for peer in peer_ports:
        delivery_table.update_probability(peer, 0.6)

    # Try to deliver an initial greeting; queue on failure
    for peer in peer_ports:
        msg = f"Hello from node {MY_PORT}"
        if not send_message(peer, msg):
            print(f"[NODE {MY_PORT}] Peer {peer} unavailable – message queued")
            with queue_lock:
                message_queue.append(msg)

    # Hand over to interactive CLI
    cli_loop()


if __name__ == "__main__":
    main()
