# Run Instructions – Week 8: Opportunistic Routing

## Prerequisites
- Python 3.10 or later
- No external packages required (uses stdlib only)

---

## Step-by-Step Lab Walkthrough

### Step 1 – Open three terminals

Each terminal represents one mobile node in the network.

---

### Step 2 – Start Node A (port 9000)

```bash
cd week08-opportunistic-routing-basic
python node.py --port 9000
```

Expected output:
```
[TABLE] Updated P(9001) = 0.60
[TABLE] Updated P(9002) = 0.60
[NODE 9000] ❌ Could not reach port 9001
[NODE 9000] Peer 9001 unavailable – message queued
[NODE 9000] ❌ Could not reach port 9002
[NODE 9000] Peer 9002 unavailable – message queued
[NODE 9000] 🔊 Listening for incoming messages...
[NODE 9000] Ready. Type 'help' for commands.
```

> Messages are queued because the other nodes aren't running yet — this is correct behaviour.

---

### Step 3 – Start Node B (port 9001)

```bash
python node.py --port 9001
```

---

### Step 4 – Start Node C (port 9002)

```bash
python node.py --port 9002
```

---

### Step 5 – Observe opportunistic forwarding

After `UPDATE_INTERVAL` (default 5 seconds), Node A's `forward_loop` will retry queued messages. You should see:

**Node A terminal:**
```
[NODE 9000] 🔍 Candidates: [9001, 9002]  Queue: 2 msg(s)
[NODE 9000] ✅ Sent: 'Hello from node 9000' → port 9001
[NODE 9000] ✅ Sent: 'Hello from node 9000' → port 9002
```

**Node B terminal:**
```
[NODE 9001] 📥 Received: 'Hello from node 9000' from 9000
```

---

### Step 6 – Experiment with probabilities

In Node A's terminal:

```
# Lower the probability below threshold
[9000]> set 9001 0.3
[9000]> send 9001 This should queue
  Message queued (1 in queue)

# Raise it back
[9000]> set 9001 0.8
# The forward_loop will deliver it within UPDATE_INTERVAL seconds
```

---

### Step 7 – Apply aging

```
[9000]> decay
[TABLE] Aging applied (γ=0.98). Table: {9001: 0.784, 9002: 0.588}
```

Run `decay` several times to watch probabilities drop. Eventually peers may fall below the threshold.

---

### Step 8 – View queue and table at any time

```
[9000]> queue
[9000]> table
```

---

## Verification Checklist

- [ ] Messages sent only to peers with P >= 0.5
- [ ] Failed deliveries appear in queue
- [ ] Queue drains automatically when peers become reachable
- [ ] Probabilities decrease after calling `decay`
- [ ] Node continues receiving messages while forward_loop runs

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Address already in use` | Change `BASE_PORT` in config.py or use `--port` flag |
| Messages never forwarded | Check `FORWARD_THRESHOLD` vs actual probabilities in `table` |
| Queue grows without draining | Ensure peer nodes are running and reachable |
