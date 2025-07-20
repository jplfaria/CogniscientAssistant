#!/bin/bash
# Development environment setup script
# Supports both traditional pip and modern uv workflows

echo "Setting up AI Co-Scientist development environment..."

# Check if uv is installed
if command -v uv &> /dev/null; then
    echo "Using uv for fast environment setup..."
    
    # Create virtual environment with uv
    uv venv
    
    # Activate instructions
    echo ""
    echo "To activate the virtual environment, run:"
    echo "  source .venv/bin/activate"
    echo ""
    
    # Install dependencies with uv
    source .venv/bin/activate
    uv pip install -e ".[dev]"
    
else
    echo "uv not found, using standard Python tools..."
    echo "Consider installing uv for faster setup: https://github.com/astral-sh/uv"
    echo ""
    
    # Traditional setup
    python -m venv venv
    
    # Activate instructions
    echo ""
    echo "To activate the virtual environment, run:"
    echo "  source venv/bin/activate"
    echo ""
    
    # Install dependencies with pip
    source venv/bin/activate
    pip install -e ".[dev]"
fi

echo ""
echo "✅ Development environment ready!"
echo ""
echo "Next steps:"
echo "1. Activate your virtual environment (see above)"
echo "2. Run tests: pytest"
echo "3. Start implementation loop: ./run-loop.sh"