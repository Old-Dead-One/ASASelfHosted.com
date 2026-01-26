"""
Database query helpers.

Common database operations using Supabase client.
All queries should respect RLS policies.

Functions accept a Client parameter rather than using globals.
This forces explicit choice of client at call sites:
- supabase_anon: Public reads
- get_rls_client(user_jwt): Authenticated RLS reads/writes
- supabase_admin: Admin operations (webhooks, maintenance)
"""

# from supabase import Client  # TODO: Implement common database query functions

# TODO: Implement common database query functions
# TODO: Server queries
# TODO: Cluster queries
# TODO: Consent queries
# TODO: Verification queries

# Example function signature pattern:
# async def list_directory_servers(
#     db: Client,
#     page: int = 1,
#     page_size: int = 50,
#     q: str | None = None,
# ):
#     """
#     List servers from directory_view.
#
#     Args:
#         db: Supabase client (use supabase_anon for public reads)
#         page: Page number (1-indexed)
#         page_size: Items per page
#         q: Optional search query
#
#     Returns:
#         List of directory servers
#     """
#     query = db.table("directory_view").select("*")
#     if q:
#         query = query.ilike("name", f"%{q}%")
#     result = query.range((page - 1) * page_size, page * page_size - 1).execute()
#     return result.data
