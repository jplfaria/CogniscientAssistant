#!/usr/bin/env python3
"""
Patched argo-proxy launcher that uses our local modifications.
This script starts argo-proxy with our Claude compatibility patch.

IMPORTANT: This is a temporary solution until the official argo-proxy
adds support for Claude's string system content requirement.
"""

import sys
import os
import subprocess

# Add our patched version to the Python path BEFORE the installed version
patched_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'patched_argoproxy')
sys.path.insert(0, os.path.dirname(patched_path))

# Now run the argo-proxy main module
if __name__ == "__main__":
    # Change to the argoproxy module directory
    os.chdir(patched_path)
    
    # Run the module
    subprocess.run([sys.executable, "-m", "argoproxy"] + sys.argv[1:])