#!/usr/bin/env python3
"""
Seed mods catalog for Ark: Survival Ascended.

Fetches top mods from CurseForge and populates the mods_catalog table.
Run manually to pre-populate the catalog with popular mods.

Usage:
    python scripts/seed_mods_catalog_asa.py
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Change to backend directory to ensure .env file is found
backend_dir = Path(__file__).parent.parent
os.chdir(backend_dir)

# Add parent directory to path for imports
sys.path.insert(0, str(backend_dir))

from app.core.config import get_settings
from app.db.mods_catalog_repo import ModCatalogEntry
from app.db.providers import get_mods_catalog_repo
from app.integrations.curseforge_client import CurseForgeClient, CurseForgeMod

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def seed_mods_catalog():
    """Seed mods catalog with top ASA mods from CurseForge."""
    settings = get_settings()

    # Validate API key
    if not settings.CURSEFORGE_API_KEY:
        logger.error("CURSEFORGE_API_KEY not set. Cannot seed mods catalog.")
        sys.exit(1)

    # Initialize client
    client = CurseForgeClient()

    try:
        # Discover ASA game ID
        logger.info("Discovering Ark: Survival Ascended game ID...")
        asa_game_id = await client.find_asa_game_id()
        logger.info(f"Found ASA game ID: {asa_game_id}")

        # Get categories
        logger.info("Fetching categories...")
        categories = await client.get_categories(game_id=asa_game_id)
        logger.info(f"Found {len(categories)} categories")

        # Collect mods from top categories
        # We'll fetch top 50 mods per category sorted by popularity
        all_mods: dict[int, CurseForgeMod] = {}
        semaphore = asyncio.Semaphore(3)  # Limit concurrency

        async def fetch_category_mods(category: dict):
            """Fetch mods for a category."""
            async with semaphore:
                category_id = category.get("id")
                category_name = category.get("name", "Unknown")
                logger.info(f"Fetching mods for category: {category_name} (ID: {category_id})")

                try:
                    mods = await client.search_mods(
                        game_id=asa_game_id,
                        category_id=category_id,
                        page_size=50,
                        sort_field="Popularity",
                    )
                    logger.info(
                        f"Found {len(mods)} mods in category {category_name}"
                    )
                    for mod in mods:
                        all_mods[mod["id"]] = mod
                except Exception as e:
                    logger.error(
                        f"Failed to fetch mods for category {category_name}: {str(e)}"
                    )

        # Fetch mods from all categories concurrently
        tasks = [fetch_category_mods(cat) for cat in categories]
        await asyncio.gather(*tasks)

        logger.info(f"Collected {len(all_mods)} unique mods")

        # Prepare catalog entries
        catalog_entries: list[ModCatalogEntry] = []
        for mod_id, mod_data in all_mods.items():
            catalog_entries.append(
                {
                    "mod_id": mod_id,
                    "name": mod_data["name"],
                    "slug": mod_data.get("slug"),
                    "source": "curseforge",
                }
            )

        # Upsert into catalog
        logger.info(f"Upserting {len(catalog_entries)} mods into catalog...")
        catalog_repo = get_mods_catalog_repo()
        await catalog_repo.upsert_many(catalog_entries)

        logger.info(
            f"Successfully seeded mods catalog with {len(catalog_entries)} mods"
        )

    except Exception as e:
        logger.error(f"Failed to seed mods catalog: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(seed_mods_catalog())
