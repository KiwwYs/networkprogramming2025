# Run Instructions – Week 9: Bio-Inspired Networking

## Prerequisites
- Python 3.10 or later
- No external packages required (stdlib only)

---

## Step-by-Step Lab Walkthrough

### Step 1 – Open three terminals

### Step 2 – Start Node A (port 10000)

```bash
python node.py --port 10000
```

Expected output:
```
[PHEROMONE] Reinforced 10001: 1.000
[PHEROMONE] Reinforced 10002: 1.000
[NODE 10000] ❌ Failed to send to 10001
[NODE 10000] Peer 10001 unavailable – queued
[NODE 10000] 🔊 Listening...
[NODE 10000] Ready.
```

### Step 3 – Start Node B and C

```bash
python node.py --port 10001
python node.py --port 10002
```

### Step 4 – Observe pheromone reinforcement

After `UPDATE_INTERVAL` (5s), Node A's `forward_loop` fires:

```
[NODE 10000] 🐜 Candidates: [10001, 10002]  Queue: 2 msg(s)
[NODE 10000] ✅ Sent: 'Hello from node 10000' → port 10001
[PHEROMONE] Reinforced 10001: 1.100
[NODE 10000] ✅ Sent: 'Hello from node 10000' → port 10002
[PHEROMONE] Reinforced 10002: 1.100
```

Each success adds `REINFORCEMENT = 0.1` to that peer's trail.

### Step 5 – Watch decay in action

Every cycle, decay fires before forwarding:

```
[PHEROMONE] Decay applied (×0.9). Table: {10001: 0.990, 10002: 0.990}
```

Stop Node B. After several cycles Node B's pheromone will decay below `FORWARD_THRESHOLD = 0.2` and be excluded from candidates.

### Step 6 – Manual experiments

```
# Drain a path manually
[10000]> decay
[10000]> decay
[10000]> decay
[10000]> pheromone

# Boost a specific path
[10000]> reinforce 10002 2.0
[10000]> pheromone
```

---

## Verification Checklist

- [ ] Messages routed along strongest pheromone trail
- [ ] Successful deliveries increase pheromone
- [ ] Failed deliveries do NOT increase pheromone
- [ ] Pheromone decreases each cycle via decay
- [ ] Paths below FORWARD_THRESHOLD are not used
- [ ] Queue drains automatically when candidates become available

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Address already in use` | Use a different `--port` value |
| Pheromone never decays below threshold | Increase number of decay cycles or reduce DECAY_FACTOR in config |
| Messages never forwarded | Check pheromone table — may all be below FORWARD_THRESHOLD |
