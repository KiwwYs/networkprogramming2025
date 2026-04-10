# Week 8 – Opportunistic Routing (Basic)

> *Forward packets based on probability, not certainty.*

---

## Concept

Traditional routing assumes fixed paths. Opportunistic routing embraces uncertainty: a node **carries** a message until it encounters another node with a high enough **delivery probability** to pass it along.

This mirrors real-world scenarios like:
- Wildlife sensor networks (sensors only meet occasionally)
- Mobile ad-hoc disaster networks (no infrastructure)
- Opportunistic IoT systems

---

## Directory Structure

```
week08-opportunistic-routing-basic/
├── README.md
├── node.py           ← main node (server + forwarder + CLI)
├── delivery_table.py ← delivery probability table
├── config.py         ← shared configuration
└── docs/
    └── run_instructions.md
```

---

## Key Concepts

| Concept | Description |
|---|---|
| **Delivery Probability** | P(peer) = likelihood this node can reach that peer |
| **Opportunistic Forwarding** | Only forward when P(peer) ≥ FORWARD_THRESHOLD |
| **Message Queue** | Store messages when no good candidate is available |
| **Aging / Decay** | Reduce probabilities over time to reflect stale encounters |

---

## Quick Start

### 1. Install (no dependencies — stdlib only)
```bash
python --version   # 3.10+
```

### 2. Run three nodes in separate terminals

**Terminal 1** (node on port 9000):
```bash
python node.py --port 9000
```

**Terminal 2** (node on port 9001):
```bash
python node.py --port 9001
```

**Terminal 3** (node on port 9002):
```bash
python node.py --port 9002
```

> See `docs/run_instructions.md` for full step-by-step walkthrough.

---

## CLI Commands

```
send <port> <message>    attempt delivery or queue on failure
queue                    show queued messages
table                    show delivery probability table
set <port> <prob>        manually update a probability (0.0–1.0)
decay                    apply probability aging (×0.98)
quit                     exit
```

### Example Session

```
[9000]> table
  Port 9001: 0.60  ████████████
  Port 9002: 0.60  ████████████

[9000]> send 9001 Hello world
[NODE 9000] ✅ Sent: 'Hello world' → port 9001

[9000]> set 9001 0.3
[TABLE] Updated P(9001) = 0.30

[9000]> send 9001 Another message
[NODE 9000] ❌ Could not reach port 9001
  Message queued (1 in queue)

[9000]> set 9001 0.8
[TABLE] Updated P(9001) = 0.80
# After UPDATE_INTERVAL seconds the forward_loop will retry automatically
```

---

## Common Mistakes

| Mistake | Why It Matters |
|---|---|
| Ignoring delivery probabilities | Messages forwarded blindly → network flooding |
| Not queuing failed messages | Lost packets when peers unavailable |
| Blocking I/O in main thread | Node can't receive while forwarding |

---

## Extension Options

| Branch | Feature |
|---|---|
| `ext-a-dynamic-prob` | Update probabilities based on encounter history (PRoPHET) |
| `ext-b-ttl` | Messages expire after a time window |
| `ext-c-logging` | Track delivery attempts, successes, failures |

---

## How It Connects Forward

- **Week 9**: Replace manual probability updates with bio-inspired reinforcement (pheromone trails)
- **Capstone**: Delay-tolerant sensor network simulation combining Weeks 7–9
