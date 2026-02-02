#!/usr/bin/env python3
"""
Helper script to find Ark: Survival Ascended game ID from CurseForge API.

This script searches through CurseForge games to find ASA and prints the game ID.
You can then add it to your .env file as CURSEFORGE_ASA_GAME_ID.

Usage:
    python scripts/find_asa_game_id.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.integrations.curseforge_client import CurseForgeClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def find_asa_game_id():
    """Find and print ASA game ID."""
    settings = get_settings()

    if not settings.CURSEFORGE_API_KEY:
        logger.error("CURSEFORGE_API_KEY not set in .env file")
        sys.exit(1)

    client = CurseForgeClient()

    try:
        logger.info("Searching for Ark: Survival Ascended game ID...")
        logger.info("This may take a moment as we search through games...")
        
        asa_game_id = await client.find_asa_game_id()
        
        print("\n" + "="*60)
        print(f"✓ Found Ark: Survival Ascended game ID: {asa_game_id}")
        print("="*60)
        print("\nAdd this to your backend/.env file:")
        print(f"CURSEFORGE_ASA_GAME_ID={asa_game_id}")
        print("\nThen re-run the seeding script.\n")

    except RuntimeError as e:
        logger.error(f"Failed to find ASA game ID: {str(e)}")
        print("\n" + "="*60)
        print("Manual lookup instructions:")
        print("="*60)
        print("1. Visit: https://www.curseforge.com/ark-survival-ascended")
        print("2. Open browser DevTools (F12) → Network tab")
        print("3. Refresh the page and look for API calls")
        print("4. Or use this curl command:")
        print(f"   curl -H 'x-api-key: {settings.CURSEFORGE_API_KEY[:10]}...' \\")
        print("        https://api.curseforge.com/v1/games | jq '.data[] | select(.slug == \"ark-survival-ascended\")'")
        print("\n")
        sys.exit(1)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(find_asa_game_id())
