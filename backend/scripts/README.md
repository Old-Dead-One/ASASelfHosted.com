# Database Scripts

Scripts for managing database data and migrations.

## insert_sample_servers.py

Inserts sample server data into the Supabase database for testing and development.

### Usage

```bash
cd backend
python scripts/insert_sample_servers.py
```

### Requirements

- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` must be set in `.env`
- The script will automatically create a test user if none exists

### What it does

1. Connects to Supabase using the service_role key (bypasses RLS)
2. Gets or creates a test user in `auth.users`
3. Inserts 5 sample servers with various configurations:
   - Vanilla PvP server
   - Modded PvE server
   - Boosted PvPvE server
   - Vanilla+ PvE server
   - Official+ Crossplay server

### Alternative: SQL Script

You can also use the SQL script directly in Supabase SQL Editor:
- `backend/app/db/migrations/004_sample_servers.sql`

This requires you to have at least one user in `auth.users` (create via Supabase Dashboard → Authentication → Users).

## test_api_endpoints.py

Comprehensive test suite for all API endpoints.

### Usage

```bash
cd backend
python scripts/test_api_endpoints.py
```

### Requirements

- Backend server must be running (default: http://localhost:5173)
- `SUPABASE_URL` and `SUPABASE_ANON_KEY` must be set in `.env`

### What it tests

- API info and health check endpoints
- List servers with various filters
- Pagination and sorting
- Search functionality
- Get single server
- Get filters endpoint
- Error handling (404 for not found)

## Validation Queries

### Validate Platforms Type

If you're seeing platforms as `"{steam,epic}"` instead of `["steam", "epic"]` in API responses:

1. Run the validation query in Supabase SQL Editor:
   - `backend/app/db/migrations/005_validate_platforms_type.sql`

2. Verify the column type is `platform[]` (not `text`)

3. The repository now includes normalization to handle Postgres array strings, but the root cause should be fixed at the database level.
