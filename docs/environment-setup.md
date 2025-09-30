# Environment Setup Guide

## Using UV for Modern Python Package Management

### 1. Install UV
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create Virtual Environment
```bash
# Create and activate virtual environment
uv venv --python 3.11
source .venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
```bash
# Install all dependencies with proper locking
uv pip install -e ".[dev]"

# Generate lock file
uv pip freeze > requirements-lock.txt
```

### 4. Development Workflow
```bash
# Always activate venv first
source .venv/bin/activate

# Install new packages
uv pip install package_name

# Update lock file after changes
uv pip freeze > requirements-lock.txt
```

### 5. CI/CD Integration
```bash
# In CI, install from lock file for reproducibility
uv pip install -r requirements-lock.txt
```

## Benefits
- ⚡ 10-100x faster than pip
- 🔒 Proper dependency locking
- 🧹 Clean virtual environments
- 🔄 Easy environment reproduction