# Week 10 – Quantum-Inspired Networking (Basic)

> *Messages may be read once, cannot be cloned, and network state collapses on access.*

---

## Concept

Quantum networking introduces ideas that have no classical equivalent — but we can *simulate* them:

| Quantum Principle | This Simulation |
|---|---|
| **No-Cloning** | A token can only be read once. Re-reading returns `None`. |
| **State Collapse** | Reading marks `token.read = True` permanently. |
| **Decoherence** | Tokens expire after `TOKEN_EXPIRY` seconds. |

No quantum hardware needed — these constraints are enforced in software.

---

## Directory Structure

```
week10-quantum-network-basic/
├── README.md
├── node.py     ← main node (server + forward_loop + CLI)
├── token.py    ← one-time-read Token class
├── config.py   ← shared configuration
└── docs/
    └── run_instructions.md
```

---

## Quick Start

```bash
# Terminal 1
python node.py --port 11000

# Terminal 2
python node.py --port 11001

# Terminal 3
python node.py --port 11002
```

> See `docs/run_instructions.md` for a full walkthrough.

---

## CLI Commands

```
create <message>       create a token and queue it
send <port> <message>  create a token and send immediately
queue                  list all tokens in queue with status
quit
```

### Example Session

```
[11000]> send 11001 Hello quantum world
[NODE 11000] 📤 Sent token a3f2b1c0 → port 11001

# On Node 11001:
[NODE 11001] 📥 Token a3f2b1c0 → 'Hello quantum world' (from port 11000)
[TOKEN a3f2b1c0] ✅ Read and consumed (state collapsed)

# Attempting to read the same token again:
[TOKEN a3f2b1c0] 🚫 Already consumed — no-cloning principle violated
```

---

## Common Mistakes

| Mistake | Why It Matters |
|---|---|
| Ignoring token state | Violates one-time-read principle |
| Not checking expiry | Stale tokens circulate indefinitely |
| Blocking the main loop | Token forwarding is delayed or lost |

---

## Extension Options

| Branch | Feature |
|---|---|
| `ext-a-expiry` | Configurable expiry per token + cleanup thread |
| `ext-b-multi-hop` | Forward tokens across multiple nodes before consumption |
| `ext-c-logging` | Log all token state transitions for visualisation |

---

## How It Connects Forward

- **Week 9**: Compared to pheromone routing — quantum tokens are *ephemeral*, not reinforced
- **Capstone**: Delay-tolerant quantum-inspired network simulator combining Weeks 8–10
