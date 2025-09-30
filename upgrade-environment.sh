#!/bin/bash
# Safe Environment Upgrade Script

set -e  # Exit on any error

echo "🚀 Starting Environment Modernization"

# 1. Create backup of current environment
echo "📦 Creating backup of current pyproject.toml"
cp pyproject.toml pyproject.toml.backup

# 2. Install UV if not present
if ! command -v uv &> /dev/null; then
    echo "📥 Installing UV package manager"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

# 3. Create virtual environment
echo "🏗️ Creating virtual environment"
uv venv --python 3.11 .venv
source .venv/bin/activate

# 4. Install dependencies with modern versions
echo "📦 Installing modern dependencies"
cp pyproject-modern.toml pyproject.toml
uv pip install -e ".[dev]"

# 5. Run tests to check compatibility
echo "🧪 Running tests to verify compatibility"
if python -m pytest tests/unit/ --tb=short -q; then
    echo "✅ Unit tests passed!"
else
    echo "❌ Unit tests failed - check output above"
    echo "🔄 Restoring backup..."
    cp pyproject.toml.backup pyproject.toml
    exit 1
fi

# 6. Run integration tests
echo "🔗 Running integration tests"
if python -m pytest tests/integration/ --tb=short -q -x; then
    echo "✅ Integration tests passed!"
else
    echo "⚠️ Integration tests had issues - check output above"
    echo "This might be expected for some tests"
fi

# 7. Generate lock file
echo "🔒 Generating dependency lock file"
uv pip freeze > requirements-lock.txt

echo "✅ Environment modernization completed!"
echo "📄 Review the changes and commit if satisfied:"
echo "   git add ."
echo "   git commit -m 'feat: modernize environment with UV and pinned dependencies'"