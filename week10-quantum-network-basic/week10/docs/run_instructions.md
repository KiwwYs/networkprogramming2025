# Run Instructions – Week 10: Quantum-Inspired Networking

## Prerequisites
- Python 3.10 or later
- No external packages required (stdlib only)

---

## Step-by-Step Lab Walkthrough

### Step 1 – Open three terminals

### Step 2 – Start Node A (port 11000)

```bash
python node.py --port 11000
```

Expected output:
```
[NODE 11000] ❌ Failed to reach port 11001
[NODE 11000] Peer 11001 unavailable – token queued
[NODE 11000] 🔊 Listening for incoming tokens...
[NODE 11000] Ready.
```

### Step 3 – Start Node B and C

```bash
python node.py --port 11001
python node.py --port 11002
```

After `UPDATE_INTERVAL` (5s), Node A's queued tokens will be forwarded:
```
[NODE 11000] 📤 Sent token a3f2b1c0 → port 11001
```

On Node B:
```
[NODE 11001] 📥 Token a3f2b1c0 → 'Quantum token from 11000' (from port 11000)
[TOKEN a3f2b1c0] ✅ Read and consumed (state collapsed)
```

---

### Step 4 – Test no-cloning enforcement

In Node A's terminal, try to send the same token concept twice:

```
[11000]> send 11001 Secret message
[NODE 11000] 📤 Sent token b7d3e2f1 → port 11001

# On Node B, token is read and consumed.
# Now create another token with same text — it gets a NEW id and fresh state:
[11000]> send 11001 Secret message
[NODE 11000] 📤 Sent token c9a4f8e0 → port 11001
```

Each `send` creates a **new** token with a fresh state.
The no-cloning rule prevents the *same token* from being read twice.

---

### Step 5 – Observe token expiry

```
[11000]> create This will expire
  Created token d1b2c3a4: 'This will expire'

# Wait 10+ seconds without sending
[11000]> queue
  Token(id=d1b2c3a4, status=expired, msg='This will expire')
```

After the next `forward_loop` cycle:
```
[NODE 11000] 🧹 Pruned 1 expired/consumed token(s)
```

---

### Step 6 – Manual token creation and queuing

```
[11000]> create Hello Node B
  Created token e5f6a7b8: 'Hello Node B'

[11000]> queue
  Token(id=e5f6a7b8, status=valid (4.8s left), msg='Hello Node B')
```

The forward_loop will attempt delivery within `UPDATE_INTERVAL` seconds.

---

## Verification Checklist

- [ ] Tokens delivered and consumed exactly once
- [ ] Re-reading a consumed token returns None
- [ ] Tokens expire after TOKEN_EXPIRY seconds
- [ ] Expired tokens pruned from queue automatically
- [ ] Each `send` creates a fresh token with a new ID

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Address already in use` | Use a different `--port` value |
| Tokens always expire before delivery | Increase `TOKEN_EXPIRY` in config.py |
| Queue never drains | Ensure peer nodes are running on the correct ports |
