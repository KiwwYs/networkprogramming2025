# Week 9 – Bio-Inspired Networking (Basic)

> *Ants and other social insects route better than we do, often under uncertainty.*

---

## Concept

Ant Colony Optimisation (ACO) uses pheromone trails to find efficient paths. Nodes in this simulation do the same:

- Successful deliveries **reinforce** the path (add pheromone)
- Every cycle, all trails **decay** (unused paths fade)
- Forwarding only happens along paths above a **threshold**

Over time, reliable paths accumulate strong trails. Unreliable ones evaporate naturally — no manual configuration needed.

---

## Directory Structure

```
week09-bio-routing-basic/
├── README.md
├── node.py             ← main node (server + forward_loop + CLI)
├── pheromone_table.py  ← reinforce, decay, get_best_candidates
├── config.py           ← shared configuration
└── docs/
    └── run_instructions.md
```

---

## Key Concepts

| Concept | Description |
|---|---|
| **Pheromone Trail** | Numeric strength representing how reliable a path is |
| **Reinforcement** | +REINFORCEMENT added on successful delivery |
| **Decay** | ×DECAY_FACTOR applied every cycle (evaporation) |
| **Threshold** | Only forward to peers with pheromone ≥ FORWARD_THRESHOLD |

---

## Quick Start

```bash
# Terminal 1
python node.py --port 10000

# Terminal 2
python node.py --port 10001

# Terminal 3
python node.py --port 10002
```

> See `docs/run_instructions.md` for a full walkthrough.

---

## CLI Commands

```
send <port> <message>      attempt delivery or queue on failure
queue                      show queued messages
pheromone                  show pheromone table
reinforce <port> <value>   manually add pheromone to a path
decay                      manually trigger one decay cycle
quit
```

### Example Session

```
[10000]> pheromone
  Port 10001: 1.000  ████████████████████
  Port 10002: 1.000  ████████████████████

[10000]> send 10001 Hello
[NODE 10000] ✅ Sent: 'Hello' → port 10001
[PHEROMONE] Reinforced 10001: 1.100

[10000]> decay
[PHEROMONE] Decay applied (×0.9). Table: {10001: 0.99, 10002: 0.9}

# After many decay cycles without sends, pheromone drops below threshold:
[10000]> pheromone
  Port 10001: 0.187  ███
  Port 10002: 0.170  ███
# forward_loop will no longer use these paths until reinforced
```

---

## Common Mistakes

| Mistake | Why It Matters |
|---|---|
| Not decaying pheromones | Old paths dominate indefinitely |
| Reinforcing failed sends | Routing logic rewarded for bad paths |
| Blocking main loop | Node can't forward and receive simultaneously |

---

## Extension Options

| Branch | Feature |
|---|---|
| `ext-a-dynamic-learning` | Update pheromones from round-trip success |
| `ext-b-multi-hop` | Store pheromones for paths beyond direct neighbours |
| `ext-c-logging` | Plot pheromone table evolution over time |

---

## How It Connects Forward

- **Week 8**: Compared to delivery probability (static) — pheromones are *dynamic*
- **Week 10**: Quantum-inspired routing (one-time tokens, no-cloning)
- **Capstone**: Hybrid bio-routing + delay-tolerant network simulator
