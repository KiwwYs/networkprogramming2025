# token.py  –  Week 10: Quantum-Inspired Networking
# ============================================================
# Simulates a quantum-inspired one-time-read message token.
#
# Two core quantum principles modelled here:
#
#   NO-CLONING    – once a token is read, it is consumed.
#                  Any further read attempt returns None.
#
#   STATE COLLAPSE – reading the token changes its state
#                   permanently (read=True). The act of
#                   observation destroys the original.
#
#   EXPIRY         – tokens have a time window. After
#                   TOKEN_EXPIRY seconds, the token is
#                   invalid regardless of read state.
#                   (Analogous to quantum decoherence.)
# ============================================================

import time
import uuid

from config import TOKEN_EXPIRY


class Token:
    def __init__(self, message: str):
        self.token_id  = str(uuid.uuid4())[:8]   # unique identifier
        self.message   = message
        self.read      = False                    # has this token been consumed?
        self.timestamp = time.time()              # creation time

    def read_token(self) -> str | None:
        """
        Attempt to read the token.

        Returns the message if:
          - Token has NOT been read before (no-cloning)
          - Token has NOT expired (within TOKEN_EXPIRY seconds)

        Returns None and prints a reason otherwise.
        Side effect: marks token as consumed (read=True).
        """
        # Check expiry first
        if time.time() - self.timestamp > TOKEN_EXPIRY:
            print(f"[TOKEN {self.token_id}] ⌛ Expired — state collapsed by decoherence")
            return None

        # Check no-cloning rule
        if self.read:
            print(f"[TOKEN {self.token_id}] 🚫 Already consumed — no-cloning principle violated")
            return None

        # Consume the token (state collapse)
        self.read = True
        print(f"[TOKEN {self.token_id}] ✅ Read and consumed (state collapsed)")
        return self.message

    def is_valid(self) -> bool:
        """Return True if the token is still readable (not read, not expired)."""
        return not self.read and (time.time() - self.timestamp <= TOKEN_EXPIRY)

    def status(self) -> str:
        if self.read:
            return "consumed"
        if time.time() - self.timestamp > TOKEN_EXPIRY:
            return "expired"
        remaining = TOKEN_EXPIRY - (time.time() - self.timestamp)
        return f"valid ({remaining:.1f}s left)"

    def __repr__(self) -> str:
        return f"Token(id={self.token_id}, status={self.status()}, msg='{self.message}')"
