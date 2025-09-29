"""Pytest configuration for AI Co-Scientist tests."""

import pytest


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--real-llm",
        action="store_true",
        default=False,
        help="Run real LLM integration tests (expensive, requires VPN)"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "real_llm: mark test as requiring real LLM access"
    )


def pytest_collection_modifyitems(config, items):
    """Skip real LLM tests unless --real-llm flag is provided."""
    if not config.getoption("--real-llm"):
        skip_real = pytest.mark.skip(reason="need --real-llm option to run")
        for item in items:
            if "real_llm" in item.keywords:
                item.add_marker(skip_real)