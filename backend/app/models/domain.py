"""
Core domain concepts.

These represent the foundational concepts of the platform.
They are documented here for reference and type hints.

Database schema is managed in Supabase migrations, not here.
These models are for code clarity and type safety only.
"""

from typing import Literal

# Verification states
VerificationState = Literal[
    "unverified",
    "pending",
    "verified",
    "revoked",
    "expired",
]

# Consent states
ConsentState = Literal[
    "granted",
    "revoked",
    "expired",
]

# Badge types (computed, never purchased)
BadgeType = Literal[
    "verified",
    "active",
    "newbie_friendly",
    "learning_friendly",
    # More badges added as features are implemented
]
