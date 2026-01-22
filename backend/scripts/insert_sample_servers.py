#!/usr/bin/env python3
"""
Insert sample servers into Supabase database.

This script uses the service_role key to bypass RLS and insert test data.
Run this from the backend directory:
    python scripts/insert_sample_servers.py
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.core.supabase import get_supabase_admin


def get_or_create_test_user(supabase_admin):
    """
    Get the first user from auth.users, or create a test user if none exists.
    """
    try:
        # Try to get existing users
        response = supabase_admin.auth.admin.list_users()
        if response and hasattr(response, 'users') and len(response.users) > 0:
            user_id = response.users[0].id
            print(f"✓ Using existing user: {user_id}")
            return user_id
    except Exception as e:
        print(f"Warning: Could not list users: {e}")

    # Create a test user
    print("Creating test user...")
    try:
        test_email = f"test-{uuid4().hex[:8]}@asaselfhosted.local"
        test_password = "TestPassword123!"
        
        response = supabase_admin.auth.admin.create_user({
            "email": test_email,
            "password": test_password,
            "email_confirm": True,
        })
        
        user_id = response.user.id
        print(f"✓ Created test user: {user_id} ({test_email})")
        return user_id
    except Exception as e:
        print(f"Error creating test user: {e}")
        raise


def insert_sample_servers(supabase_admin, owner_user_id):
    """
    Insert sample servers into the database.
    
    Note on is_verified vs status_source semantics:
    - status_source: Where the status came from (manual entry vs agent detection)
    - is_verified: Listing trust flag (curated/verified listing, regardless of status source)
    
    These are independent:
    - status_source="manual" + is_verified=True = Manually entered status, but listing is verified/curated
    - status_source="agent" + is_verified=True = Agent-detected status, listing is verified/curated
    - status_source="manual" + is_verified=False = Manually entered status, listing not verified
    """
    
    servers = [
        {
            "owner_user_id": owner_user_id,
            "name": "Island PvP Server",
            "description": "A classic vanilla PvP experience on The Island. Active community, regular events!",
            "map_name": "The Island",
            "join_address": "192.168.1.100:7777",
            "join_instructions_pc": "Open ARK, click 'Join ARK', search for 'Island PvP Server'",
            "join_instructions_console": "Search for 'Island PvP Server' in server browser",
            "mod_list": [],
            "rates": "1x Harvest, 1x XP, 1x Taming",
            "wipe_info": "Monthly wipes on the 1st",
            "pvp_enabled": True,
            "vanilla": True,
            "effective_status": "online",
            "status_source": "manual",
            "last_seen_at": "2024-01-15T10:00:00Z",
            "confidence": "green",
            "ruleset": "vanilla",
            "game_mode": "pvp",
            "platforms": ["steam", "epic"],
            "players_capacity": 70,
            "is_official_plus": False,
            "is_crossplay": False,
            "is_console": False,
            "is_pc": True,
            "is_verified": False,
            "players_current": 45,
            "quality_score": 85.5,
            "uptime_percent": 98.2,
        },
        {
            "owner_user_id": owner_user_id,
            "name": "Modded PvE Paradise",
            "description": "Heavily modded PvE server with quality of life improvements. Perfect for casual players!",
            "map_name": "The Island",
            "join_address": "192.168.1.101:7777",
            "join_instructions_pc": "Subscribe to mods: 123456789, 987654321, 555555555",
            "mod_list": ["S+ Structures", "Dino Storage v2", "Awesome Spyglass"],
            "rates": "5x Harvest, 10x XP, 15x Taming",
            "wipe_info": "No wipes planned",
            "pvp_enabled": False,
            "vanilla": False,
            "effective_status": "online",
            "status_source": "agent",
            "last_seen_at": "2024-01-15T12:30:00Z",
            "confidence": "green",
            "ruleset": "modded",
            "game_mode": "pve",
            "platforms": ["steam"],
            "players_capacity": 50,
            "is_official_plus": False,
            "is_crossplay": False,
            "is_console": False,
            "is_pc": True,
            "is_verified": True,
            "players_current": 32,
            "quality_score": 92.0,
            "uptime_percent": 99.5,
        },
        {
            "owner_user_id": owner_user_id,
            "name": "Scorched Earth Boosted",
            "description": "Boosted rates on Scorched Earth. PvP during weekdays, PvE on weekends!",
            "map_name": "Scorched Earth",
            "join_address": "192.168.1.102:7777",
            "join_instructions_pc": "Direct connect: 192.168.1.102:7777",
            "join_instructions_console": "Search 'Scorched Earth Boosted'",
            "mod_list": [],
            "rates": "3x Harvest, 5x XP, 8x Taming",
            "wipe_info": "Bi-weekly wipes",
            "pvp_enabled": True,
            "vanilla": False,
            "effective_status": "online",
            "status_source": "manual",
            "last_seen_at": "2024-01-15T11:00:00Z",
            "confidence": "yellow",
            "ruleset": "boosted",
            "game_mode": "pvpve",
            "platforms": ["steam", "xbox", "playstation"],
            "players_capacity": 100,
            "is_official_plus": False,
            "is_crossplay": True,
            "is_console": True,
            "is_pc": True,
            "is_verified": False,
            "players_current": 67,
            "quality_score": 78.3,
            "uptime_percent": 95.0,
        },
        {
            "owner_user_id": owner_user_id,
            "name": "Vanilla+ PvE Community",
            "description": "Vanilla experience with quality of life improvements. Great for beginners!",
            "map_name": "The Island",
            "join_address": "192.168.1.103:7777",
            "join_instructions_pc": "Join via server browser",
            "join_instructions_console": "Join via server browser",
            "mod_list": [],
            "rates": "1x Harvest, 2x XP, 2x Taming",
            "wipe_info": "Seasonal wipes",
            "pvp_enabled": False,
            "vanilla": True,
            "effective_status": "online",
            "status_source": "manual",
            "last_seen_at": "2024-01-15T12:45:00Z",
            "confidence": "green",
            "ruleset": "vanilla_qol",
            "game_mode": "pve",
            "platforms": ["steam", "windows_store"],
            "players_capacity": 40,
            "is_official_plus": False,
            "is_crossplay": False,
            "is_console": False,
            "is_pc": True,
            "is_verified": True,
            "players_current": 28,
            "quality_score": 88.7,
            "uptime_percent": 97.8,
        },
        {
            "owner_user_id": owner_user_id,
            "name": "Official+ Crossplay Server",
            "description": "Official-like experience with crossplay support. All platforms welcome!",
            "map_name": "The Island",
            "join_address": "192.168.1.104:7777",
            "join_instructions_pc": "Crossplay enabled - join from any platform",
            "join_instructions_console": "Crossplay enabled - join from any platform",
            "mod_list": [],
            "rates": "1x Harvest, 1x XP, 1x Taming",
            "wipe_info": "No wipes",
            "pvp_enabled": True,
            "vanilla": True,
            "effective_status": "online",
            "status_source": "agent",
            "last_seen_at": "2024-01-15T12:55:00Z",
            "confidence": "green",
            "ruleset": "vanilla",
            "game_mode": "pvp",
            "platforms": ["steam", "xbox", "playstation", "windows_store", "epic"],
            "players_capacity": 100,
            "is_official_plus": True,
            "is_crossplay": True,
            "is_console": True,
            "is_pc": True,
            "is_verified": True,
            "players_current": 89,
            "quality_score": 95.2,
            "uptime_percent": 99.9,
        },
    ]
    
    print(f"\nInserting {len(servers)} sample servers...")
    
    inserted_count = 0
    for server in servers:
        try:
            response = supabase_admin.table("servers").insert(server).execute()
            if response.data:
                inserted_count += 1
                print(f"  ✓ Inserted: {server['name']}")
            else:
                print(f"  ✗ Failed to insert: {server['name']}")
        except Exception as e:
            print(f"  ✗ Error inserting {server['name']}: {e}")
    
    print(f"\n✓ Successfully inserted {inserted_count}/{len(servers)} servers")
    return inserted_count


def main():
    """Main entry point."""
    settings = get_settings()
    
    # Check service role key
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        print("Error: SUPABASE_SERVICE_ROLE_KEY not set in .env file")
        print("This script requires the service_role key to bypass RLS")
        sys.exit(1)
    
    # Get admin client
    supabase_admin = get_supabase_admin()
    if not supabase_admin:
        print("Error: Failed to initialize Supabase admin client")
        sys.exit(1)
    
    print("✓ Connected to Supabase")
    
    # Get or create test user
    try:
        owner_user_id = get_or_create_test_user(supabase_admin)
    except Exception as e:
        print(f"Error: Failed to get/create test user: {e}")
        sys.exit(1)
    
    # Insert sample servers
    try:
        count = insert_sample_servers(supabase_admin, owner_user_id)
        print(f"\n✓ Done! Inserted {count} servers")
        print("\nYou can now query the directory endpoint:")
        print("  curl http://localhost:5173/api/v1/directory/servers")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
