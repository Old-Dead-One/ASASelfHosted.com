# Running SQL Migrations from CLI

This guide shows how to run SQL migration files from the command line instead of using the Supabase Dashboard.

## Method 1: Using `psql` (PostgreSQL CLI)

### Prerequisites

1. Install PostgreSQL client tools (if not already installed):
   ```bash
   # macOS (Homebrew)
   brew install libpq
   brew link --force libpq
   # Or full PostgreSQL (includes psql):
   brew install postgresql@16
   ```
   Then ensure `psql` is on your PATH (Homebrew often adds it to `/opt/homebrew/opt/libpq/bin/` or `/usr/local/opt/libpq/bin/`).

2. Get your Supabase database connection string:
   - Go to Supabase Dashboard → Settings → Database
   - Find "Connection string" section
   - Copy the "URI" connection string (looks like: `postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres`)

### Running a Single Migration

```bash
# Set your connection string as an environment variable
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres"

# Run a migration file
psql "$DATABASE_URL" -f backend/app/db/migrations/012_security_fixes.sql
```

### Running All Migrations in Order

```bash
# Set your connection string
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres"

# Run migrations in order
psql "$DATABASE_URL" -f backend/app/db/migrations/001_sprint_0_schema.sql
psql "$DATABASE_URL" -f backend/app/db/migrations/003_sprint_3_directory_view.sql
psql "$DATABASE_URL" -f backend/app/db/migrations/006_sprint_4_agent_auth.sql
psql "$DATABASE_URL" -f backend/app/db/migrations/012_security_fixes.sql
```

### Using a Script

Create a script to run all migrations:

```bash
#!/bin/bash
# run_migrations.sh

DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres"

MIGRATIONS=(
  "001_sprint_0_schema.sql"
  "003_sprint_3_directory_view.sql"
  "006_sprint_4_agent_auth.sql"
  "012_security_fixes.sql"
)

for migration in "${MIGRATIONS[@]}"; do
  echo "Running $migration..."
  psql "$DATABASE_URL" -f "backend/app/db/migrations/$migration"
  if [ $? -ne 0 ]; then
    echo "Error running $migration"
    exit 1
  fi
  echo "✓ $migration completed"
done

echo "All migrations completed successfully!"
```

Make it executable and run:
```bash
chmod +x run_migrations.sh
./run_migrations.sh
```

## Method 2: Using Supabase CLI

### Prerequisites

1. Install Supabase CLI:
   ```bash
   # macOS (Homebrew)
   brew install supabase/tap/supabase
   
   # npm
   npm install -g supabase
   
   # Or download from: https://github.com/supabase/cli/releases
   ```

2. Link your project:
   ```bash
   supabase link --project-ref [YOUR_PROJECT_REF]
   ```

### Running Migrations

```bash
# Run a single migration file
supabase db execute -f backend/app/db/migrations/012_security_fixes.sql

# Or if you have migrations in a local Supabase setup
supabase migration up
```

## Method 3: Using Python Script (if you have backend environment)

You can also create a simple Python script to run migrations:

```python
#!/usr/bin/env python3
# run_migration.py

import os
import sys
import psycopg2
from pathlib import Path

def run_migration(migration_file: str, database_url: str):
    """Run a SQL migration file."""
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        with open(migration_file, 'r') as f:
            sql = f.read()
            cursor.execute(sql)
        print(f"✓ Successfully ran {migration_file}")
    except Exception as e:
        print(f"✗ Error running {migration_file}: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    migration_file = sys.argv[1] if len(sys.argv) > 1 else None
    if not migration_file:
        print("Usage: python run_migration.py <migration_file.sql>")
        sys.exit(1)
    
    run_migration(migration_file, database_url)
```

Usage:
```bash
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres"
python run_migration.py backend/app/db/migrations/012_security_fixes.sql
```

## Method 4: Using `curl` with Supabase REST API

**Note:** This method is more limited and not recommended for complex migrations, but can work for simple SQL:

```bash
# Get your Supabase project URL and service role key
SUPABASE_URL="https://[PROJECT_REF].supabase.co"
SERVICE_ROLE_KEY="your_service_role_key"

# Read SQL file and execute via REST API
SQL=$(cat backend/app/db/migrations/012_security_fixes.sql)

curl -X POST \
  "$SUPABASE_URL/rest/v1/rpc/exec_sql" \
  -H "apikey: $SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$SQL\"}"
```

**Warning:** This method may not work for all SQL statements and is not officially supported.

## Security Best Practices

1. **Never commit connection strings or passwords to version control**
   - Use environment variables
   - Use `.env` files (and add them to `.gitignore`)

2. **Use service role key only for migrations**
   - Service role key bypasses RLS - use carefully
   - Prefer using the database password from Supabase Dashboard

3. **Test migrations on a development database first**
   - Always test migrations before running on production

## Getting Your Connection String

### Option 1: From Supabase Dashboard

1. Go to Supabase Dashboard → Settings → Database
2. Scroll to "Connection string"
3. Select "URI" tab
4. Copy the connection string
5. Replace `[YOUR-PASSWORD]` with your actual database password

### Option 2: Construct It Manually

Format:
```
postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
```

Where:
- `[PASSWORD]` = Your database password (set when creating the project)
- `[PROJECT_REF]` = Your project reference (found in Supabase Dashboard URL)

Example:
```
postgresql://postgres:mypassword123@db.abcdefghijklmnop.supabase.co:5432/postgres
```

## Troubleshooting

### "psql: command not found"
- Install PostgreSQL client tools (see Prerequisites above)

### "password authentication failed"
- Verify your database password is correct
- Check if you're using the right connection string format

### "permission denied"
- Ensure you're using the database password (not API keys)
- Service role key won't work with `psql` - use database password

### "relation does not exist"
- Run migrations in order (001, 003, 006, then 012)
- Check that previous migrations completed successfully

### "syntax error"
- Verify the SQL file is valid
- Check for any special characters that need escaping
- Some SQL features may not be supported in Supabase (check Supabase docs)

## macOS Quick Start

```bash
# 1. Install psql (if needed)
brew install libpq && brew link --force libpq

# 2. Get connection string from Supabase: Settings → Database → URI

# 3. Run a migration
export DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres"
psql "$DATABASE_URL" -f backend/app/db/migrations/012_security_fixes.sql
```

If `psql` is not found after install, use the full path or add to PATH:
```bash
export PATH="/opt/homebrew/opt/libpq/bin:$PATH"   # Apple Silicon
# or
export PATH="/usr/local/opt/libpq/bin:$PATH"     # Intel Mac
```

## Recommended Approach

For this project, **Method 1 (psql)** is recommended because:
- Simple and reliable
- Works with any PostgreSQL database
- Easy to script and automate
- Full SQL support

Example workflow:
```bash
# 1. Set connection string once
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres"

# 2. Run migration
psql "$DATABASE_URL" -f backend/app/db/migrations/012_security_fixes.sql

# 3. Verify (optional)
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM server_secrets;"
```
