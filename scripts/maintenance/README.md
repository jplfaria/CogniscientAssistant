# Maintenance Scripts

Scripts for fixing issues and maintaining the codebase.

## Scripts

### fix-baml-issues.py
Automated fixes for common BAML configuration issues.

**Features:**
- Adds enum aliases for case-insensitive matching
- Fixes client configurations to match test expectations
- Creates/updates environment variable mappings
- Adds test configurations to functions.baml

**What it fixes:**
1. Enum case sensitivity (e.g., `Mechanistic` → adds `@alias("mechanistic")`)
2. Missing DefaultClient with environment variables
3. Missing ArgoClient configuration (commented)
4. Environment.baml structure and variables
5. Test client retry configurations

**Usage:**
```bash
python ./scripts/maintenance/fix-baml-issues.py
```

**Files modified:**
- `baml_src/models.baml` - Adds enum aliases
- `baml_src/clients.baml` - Fixes client configurations
- `baml_src/environment.baml` - Creates/updates env mappings
- `baml_src/functions.baml` - Adds test configurations

**Safety:**
- Always creates backups before modifying files
- Shows what changes were made
- Idempotent (safe to run multiple times)

## When to Use

Run maintenance scripts when:
- Tests fail due to BAML configuration issues
- After updating BAML schemas
- When adding new environment variables
- Before running the implementation loop after BAML changes