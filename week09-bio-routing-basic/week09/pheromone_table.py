# pheromone_table.py  –  Week 9: Bio-Inspired Networking
# ============================================================
# Simulates an ant-colony pheromone trail table.
#
# Rules:
#   REINFORCE  – successful delivery adds pheromone to that path
#   DECAY      – all pheromones shrink each cycle (stale paths fade)
#   SELECT     – only paths above FORWARD_THRESHOLD are used
#
# This mirrors ACO (Ant Colony Optimisation):
#   - Good paths accumulate pheromone → preferred
#   - Unused paths decay → pruned naturally
# ============================================================

from config import DECAY_FACTOR


class PheromoneTable:
    def __init__(self):
        self.table = {}  # {peer_port: pheromone_value}

    def reinforce(self, peer: int, value: float) -> None:
        """
        Add *value* pheromone to *peer*'s trail.
        Call this on every successful delivery to reinforce the path.
        """
        self.table[peer] = self.table.get(peer, 0.0) + value
        print(f"[PHEROMONE] Reinforced {peer}: {self.table[peer]:.3f}")

    def decay(self) -> None:
        """
        Apply evaporation to all pheromone trails.
        Paths that are not reinforced will eventually drop below threshold.
        """
        for peer in self.table:
            self.table[peer] *= DECAY_FACTOR
        print(f"[PHEROMONE] Decay applied (×{DECAY_FACTOR}). "
              f"Table: { {p: round(v, 3) for p, v in self.table.items()} }")

    def get_best_candidates(self, threshold: float) -> list[int]:
        """
        Return peers with pheromone >= threshold,
        sorted by pheromone descending (strongest trail first).
        """
        candidates = [
            peer for peer, pher in self.table.items()
            if pher >= threshold
        ]
        return sorted(candidates, key=lambda p: self.table[p], reverse=True)

    def display(self) -> None:
        """Print the pheromone table with a visual bar."""
        if not self.table:
            print("[PHEROMONE] (empty)")
            return
        print("[PHEROMONE] Current trails:")
        for peer, val in sorted(self.table.items()):
            bar = "█" * min(int(val * 20), 40)
            print(f"  Port {peer}: {val:.3f}  {bar}")
