# Argo-Proxy 2.7.6 Backup and Restore Instructions

**Backup Date**: September 28, 2025
**Reason**: Before upgrading to argo-proxy 2.7.7

## Current Installation Details

- **Version**: 2.7.6 (editable install)
- **Source Location**: `/Users/jplfaria/repos/CONCORDIA/argo-proxy-repo`
- **Branch**: main
- **Install Type**: Editable install from local git repository
- **Python Environment**: `/Users/jplfaria/miniconda3/bin/python`

## What's Backed Up

1. **`current_source_code/`** - Complete copy of your argo-proxy source code repository
2. **`argo_proxy-2.7.6.dist-info/`** - Package metadata from pip
3. **`current_installation_info.txt`** - Output of `pip show argo-proxy`
4. **`current_packages.txt`** - All related packages
5. **`environment_info.txt`** - Python environment details

## How to Restore (If Needed)

### Option 1: Reinstall from Backup Source
```bash
# Uninstall current version
pip uninstall argo-proxy -y

# Reinstall from backed up source
cd /Users/jplfaria/repos/CogniscientAssistant/backups/argo-proxy-pre-2.7.7/current_source_code
pip install -e .

# Verify installation
argo-proxy --version  # Should show 2.7.6
```

### Option 2: Restore Original Source Location
```bash
# If original source location is missing/broken
cd /Users/jplfaria/repos/CONCORDIA/
rm -rf argo-proxy-repo  # Only if needed
cp -r /Users/jplfaria/repos/CogniscientAssistant/backups/argo-proxy-pre-2.7.7/current_source_code argo-proxy-repo

# Reinstall editable
pip uninstall argo-proxy -y
cd /Users/jplfaria/repos/CONCORDIA/argo-proxy-repo
pip install -e .
```

### Option 3: Quick Rollback Commands
```bash
# If 2.7.7 causes issues, run these commands:
pip uninstall argo-proxy -y
cd /Users/jplfaria/repos/CogniscientAssistant/backups/argo-proxy-pre-2.7.7/current_source_code
pip install -e .
echo "Restored to argo-proxy 2.7.6 from backup"
```

## Verification After Restore

1. **Check version**: `argo-proxy --version` should show `2.7.6`
2. **Test basic functionality**: `argo-proxy --help`
3. **Check your BAML integration**: Run a simple test
4. **Verify config**: Make sure your config file still works

## Configuration Files

Your argo-proxy configuration files are separate and should not be affected:
- `~/.config/argoproxy/config.yaml`
- Any custom config files you use

## Current Working Branch Info

Your current installation was from:
- Repository: `https://gitlab.osti.gov/ai-at-argonne/argo-gateway-api/argo-proxy-tools/argo-openai-proxy.git`
- Branch: `main`
- Last commit: `d93d319 Sync from dev upstream`

## Notes

- Your installation was an **editable install** (`pip install -e .`)
- This means changes to the source code directly affect the installed package
- The backup preserves your exact working state
- You can safely upgrade and restore if needed

## Troubleshooting

If restoration fails:
1. Check that Python environment is the same: `/Users/jplfaria/miniconda3/bin/python`
2. Make sure you're in the right directory when running `pip install -e .`
3. Check file permissions on the backed up source code
4. Verify that git is working in the restored directory

## Emergency Rollback Script

Save this as a script for quick rollback:
```bash
#!/bin/bash
echo "Rolling back to argo-proxy 2.7.6..."
pip uninstall argo-proxy -y
cd /Users/jplfaria/repos/CogniscientAssistant/backups/argo-proxy-pre-2.7.7/current_source_code
pip install -e .
echo "Rollback complete. Testing..."
argo-proxy --version
```