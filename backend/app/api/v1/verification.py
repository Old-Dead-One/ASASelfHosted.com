"""
Verification endpoints.

Handles cryptographic verification of servers and clusters.
Verification is trust-based, not payment-based.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/verification", tags=["verification"])


@router.post("/initiate")
async def initiate_verification():
    """
    Initiate verification process for a server or cluster.

    Returns verification challenge that must be signed with server's private key.
    """
    # TODO: Implement verification initiation
    pass


@router.post("/verify")
async def verify_signature():
    """
    Submit signed verification challenge.

    Verifies cryptographic signature matches server's public key.
    Updates verification status on success.
    """
    # TODO: Implement signature verification
    pass


@router.get("/status/{server_id}")
async def get_verification_status(server_id: str):
    """
    Get verification status for a server or cluster.
    """
    # TODO: Implement verification status check
    pass
