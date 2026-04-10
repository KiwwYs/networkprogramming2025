#!/usr/bin/env python3
# node.py  –  Week 10: Quantum-Inspired Networking
# ============================================================
# Nodes exchange one-time-read tokens.
#
# Key behaviours:
#   - Tokens are created with a message and timestamp
#   - A token can only be READ ONCE (no-cloning)
#   - Tokens expire after TOKEN_EXPIRY seconds (decoherence)
#   - Forwarding a token to another node does NOT read it —
#     only the receiving node's server reads it on arrival
#   - Attempting to re-send a consumed token is blocked
#
# Run multiple nodes in separate terminals:
#   python node.py --port 11000
#   python node.py --port 11001
#   python node.py --port 11002
#
# Common mistakes this code addresses:
#   ✓ Token state checked before every send/receive
#   ✓ Expired tokens removed from queue automatically
#   ✓ Server and forward_loop run in separate threads
# ============================================================

import socket
import threading
import time
import argparse

from config import HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE, UPDATE_INTERVAL
from token import Token

# ------------------------------------------------------------------
# Shared state
# ------------------------------------------------------------------
token_queue: list[Token] = []
queue_lock = threading.Lock()

MY_PORT: int = BASE_PORT


# ============================  Networking  ========================

def send_token(peer_port: int, token: Token) -> bool:
    """
    Send a token's message to *peer_port*.
    The raw message string is transmitted; the receiving node
    wraps it in a new Token (state is local to each node).

    Only attempts to send if the token is still valid.
    """
    if not token.is_valid():
        print(f"[NODE {MY_PORT}] ⚠️  Token {token.token_id} no longer valid — skipping")
        return False

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        # Transmit: "TOKEN_ID|message" so receiver can log the origin ID
        payload = f"{token.token_id}|{token.message}"
        s.sendall(payload.encode())
        s.close()
        print(f"[NODE {MY_PORT}] 📤 Sent token {token.token_id} → port {peer_port}")
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        print(f"[NODE {MY_PORT}] ❌ Failed to reach port {peer_port}")
        return False


def start_server() -> None:
    """
    TCP server: receive token payloads, wrap in Token, attempt read.
    If readable, add to queue for potential re-forwarding.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, MY_PORT))
    server.listen(5)
    print(f"[NODE {MY_PORT}] 🔊 Listening for incoming tokens...")

    while True:
        conn, addr = server.accept()
        data = conn.recv(BUFFER_SIZE).decode().strip()
        conn.close()

        if not data:
            continue

        # Parse payload
        if "|" in data:
            origin_id, message = data.split("|", 1)
        else:
            origin_id, message = "unknown", data

        # Wrap in a fresh Token (new local state)
        token = Token(message)
        result = token.read_token()

        if result:
            print(f"[NODE {MY_PORT}] 📥 Token {origin_id} → '{result}' (from port {addr[1]})")
            # Store consumed token in queue for logging purposes
            # (token.read=True, so forward_loop will not re-send it)
            with queue_lock:
                token_queue.append(token)
        else:
            print(f"[NODE {MY_PORT}] 🚫 Token {origin_id} invalid from port {addr[1]}")


# ============================  Forwarding  ========================

def forward_loop() -> None:
    """
    Forwarding loop with one-time-read enforcement.

    Each cycle:
      1. Remove expired or consumed tokens from queue
      2. For remaining valid tokens, attempt delivery to peers
      3. Remove successfully forwarded tokens
    """
    while True:
        time.sleep(UPDATE_INTERVAL)

        with queue_lock:
            # Prune invalid tokens
            before = len(token_queue)
            token_queue[:] = [t for t in token_queue if t.is_valid()]
            pruned = before - len(token_queue)
            if pruned:
                print(f"[NODE {MY_PORT}] 🧹 Pruned {pruned} expired/consumed token(s)")

            valid = [t for t in token_queue if t.is_valid()]

        if not valid:
            continue

        print(f"[NODE {MY_PORT}] 🔁 Forwarding {len(valid)} valid token(s)...")

        forwarded = []
        for token in valid:
            for peer in PEER_PORTS:
                if peer == MY_PORT:
                    continue
                if send_token(peer, token):
                    forwarded.append(token)
                    break   # Token sent — do not send to multiple peers (no-cloning)

        with queue_lock:
            for t in forwarded:
                if t in token_queue:
                    token_queue.remove(t)


# ============================  CLI  ================================

def cli_loop() -> None:
    """
    Interactive CLI.

    Commands:
        create <message>    create a new token and queue it
        send <port> <msg>   create token and send immediately
        queue               show all tokens in queue
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
            print("  create <message>       create token and queue it")
            print("  send <port> <message>  create token and send immediately")
            print("  queue                  list all tokens in queue")
            print("  quit")

        elif cmd == "create" and len(parts) >= 2:
            message = parts[1] if len(parts) == 2 else " ".join(parts[1:])
            token = Token(message)
            with queue_lock:
                token_queue.append(token)
            print(f"  Created token {token.token_id}: '{message}'")

        elif cmd == "send" and len(parts) >= 3:
            try:
                peer_port = int(parts[1])
                message   = parts[2]
            except ValueError:
                print("  Usage: send <port> <message>")
                continue
            token = Token(message)
            if not send_token(peer_port, token):
                with queue_lock:
                    token_queue.append(token)
                print(f"  Token queued ({len(token_queue)} in queue)")

        elif cmd == "queue":
            with queue_lock:
                if token_queue:
                    for t in token_queue:
                        print(f"  {t}")
                else:
                    print("  (empty)")

        elif cmd == "quit":
            break

        else:
            print("  Unknown command. Type 'help'.")


# ============================  Main  ==============================

def main() -> None:
    global MY_PORT

    parser = argparse.ArgumentParser(description="Week 10 – Quantum-Inspired Networking Node")
    parser.add_argument("--port", type=int, default=BASE_PORT,
                        help=f"Port for this node (default: {BASE_PORT})")
    args = parser.parse_args()
    MY_PORT = args.port

    # Start background threads
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # Create and send an initial token to each peer
    for peer in PEER_PORTS:
        if peer == MY_PORT:
            continue
        token = Token(f"Quantum token from {MY_PORT}")
        if not send_token(peer, token):
            print(f"[NODE {MY_PORT}] Peer {peer} unavailable – token queued")
            with queue_lock:
                token_queue.append(token)

    cli_loop()


if __name__ == "__main__":
    main()
