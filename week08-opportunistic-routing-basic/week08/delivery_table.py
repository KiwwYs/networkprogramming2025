# delivery_table.py  –  Week 8: Opportunistic Routing
# ============================================================
# Maintains delivery probability for each known peer.
#
# Delivery probability P(peer) represents how likely this node
# is to successfully deliver a message to that peer based on
# past encounter history.
#
# Higher P → more reliable path → preferred for forwarding.
# ============================================================


class DeliveryTable:
    def __init__(self):
        self.table = {}  # {peer_port: probability}

    def update_probability(self, peer: int, prob: float) -> None:
        """
        Set or update the delivery probability for a peer.

        In a real PRoPHET-style system this would be:
            P_new = P_old + (1 - P_old) * P_INIT   on direct encounter
            P_new = P_old * GAMMA                   on aging
        For the basic lab we accept an explicit probability value.

        Args:
            peer: port number identifying the peer node
            prob: probability value in [0.0, 1.0]
        """
        prob = max(0.0, min(1.0, prob))   # clamp to valid range
        self.table[peer] = prob
        print(f"[TABLE] Updated P({peer}) = {prob:.2f}")

    def get_probability(self, peer: int) -> float:
        """Return delivery probability for peer, defaulting to 0.0."""
        return self.table.get(peer, 0.0)

    def get_best_candidates(self, threshold: float) -> list[int]:
        """
        Return list of peers whose delivery probability >= threshold,
        sorted by probability descending (best candidates first).
        """
        candidates = [
            peer for peer, prob in self.table.items()
            if prob >= threshold
        ]
        return sorted(candidates, key=lambda p: self.table[p], reverse=True)

    def decay_all(self, gamma: float = 0.98) -> None:
        """
        Apply aging (decay) to all probabilities.
        Call periodically to reduce probabilities of peers not recently seen.
        """
        for peer in self.table:
            self.table[peer] *= gamma
        print(f"[TABLE] Aging applied (γ={gamma}). Table: {self.table}")

    def display(self) -> None:
        """Print the full delivery probability table."""
        if not self.table:
            print("[TABLE] (empty)")
            return
        print("[TABLE] Current delivery probabilities:")
        for peer, prob in sorted(self.table.items()):
            bar = "█" * int(prob * 20)
            print(f"  Port {peer}: {prob:.2f}  {bar}")
