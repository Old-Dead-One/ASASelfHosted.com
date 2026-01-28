# Hosting Provider Migration – Verification Checklist

Run after applying `013_sprint_6_hosting_provider.sql`.

## 1. DB checks

### Column exists and defaults

```sql
SELECT hosting_provider, count(*)
FROM public.servers
GROUP BY hosting_provider;
```

- Expect `self_hosted` for existing rows (default).
- If you manually set some to `official` or `nitrado`, they won't appear in directory.

### Directory excludes non–self-hosted (Nitrado and Official)

1. Insert test servers with `hosting_provider = 'nitrado'` and `hosting_provider = 'official'` (use service role or DB user):

```sql
-- Get an existing owner_user_id from servers, or use a known UUID
INSERT INTO public.servers (
    owner_user_id,
    name,
    hosting_provider
) VALUES 
    ((SELECT owner_user_id FROM servers LIMIT 1), 'Test Nitrado Server', 'nitrado'),
    ((SELECT owner_user_id FROM servers LIMIT 1), 'Test Official Server', 'official')
RETURNING id, name, hosting_provider;
```

2. Confirm they do **not** appear in `directory_view`:

```sql
SELECT id, name FROM directory_view
WHERE name IN ('Test Nitrado Server', 'Test Official Server');
```

- Expected: 0 rows. (Directory view filters to `hosting_provider = 'self_hosted'` only; it does not expose the column.)

4. (Optional) Delete the test rows:

```sql
DELETE FROM servers WHERE name IN ('Test Nitrado Server', 'Test Official Server');
```

## 2. API checks

### Public directory returns only self_hosted

```bash
curl -s "http://localhost:5173/api/v1/directory/servers?limit=5" | jq '.data[] | {id, name, hosting_provider}'
```

- Every item must have `hosting_provider: "self_hosted"`.

### Single-server fetch

```bash
# Use an ID from the directory list
curl -s "http://localhost:5173/api/v1/directory/servers/<SERVER_ID>" | jq '.hosting_provider'
```

- Expected: `"self_hosted"`.

## 3. Owner / “my servers” views

- If you have owner-specific endpoints that read from `servers` (not `directory_view`), they can still return all rows, including `nitrado` / `official` / `other_managed`.
- Directory API must only return `self_hosted` (enforced via `directory_view`).

## 4. Quick verification script

Run against your DB (replace `$DATABASE_URL`):

```bash
export DATABASE_URL="postgresql://..."

# 1. Column and counts
psql "$DATABASE_URL" -c "
  SELECT hosting_provider, count(*) FROM public.servers GROUP BY hosting_provider;
"

# 2. Directory view only self_hosted
psql "$DATABASE_URL" -c "
  SELECT DISTINCT hosting_provider FROM directory_view;
"
```

- Column exists, counts look correct, and `directory_view` only has `self_hosted`.
