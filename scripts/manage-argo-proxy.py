#!/usr/bin/env python3
"""
Argo Proxy Management Script
Easily switch between different Argo proxy implementations.
"""

import os
import sys
import subprocess
import signal
from pathlib import Path
# import psutil  # Removed dependency

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
PID_DIR = PROJECT_DIR / ".pids"
PID_DIR.mkdir(exist_ok=True)

PROXY_CONFIGS = {
    "fixed": {
        "name": "Fixed Argo Proxy (patched official)",
        "script": "argo-proxy-fixed.py",
        "port": 8000,
        "pid_file": PID_DIR / "argo-proxy-fixed.pid",
        "env_url": "http://localhost:8000/v1"
    },
    "custom": {
        "name": "Custom Argo Proxy (CONCORDIA-style)",
        "script": "custom-argo-proxy.py",
        "port": 8000,
        "pid_file": PID_DIR / "custom-argo-proxy.pid",
        "env_url": "http://localhost:8000/v1"
    }
}

def is_port_in_use(port):
    """Check if a port is in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('', port))
            return False
        except:
            return True

def stop_proxy(proxy_type):
    """Stop a running proxy."""
    config = PROXY_CONFIGS.get(proxy_type)
    if not config:
        print(f"❌ Unknown proxy type: {proxy_type}")
        return False
    
    pid_file = config["pid_file"]
    
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, signal.SIGTERM)
            pid_file.unlink()
            print(f"✅ Stopped {config['name']} (PID: {pid})")
            return True
        except (ProcessLookupError, ValueError):
            pid_file.unlink()
            print(f"⚠️  {config['name']} was not running (cleaned up pid file)")
    
    # Also check if port is in use
    if is_port_in_use(config["port"]):
        print(f"⚠️  Port {config['port']} is still in use. You may need to kill the process manually.")
        return False
    
    return True

def start_proxy(proxy_type):
    """Start a proxy."""
    config = PROXY_CONFIGS.get(proxy_type)
    if not config:
        print(f"❌ Unknown proxy type: {proxy_type}")
        return False
    
    # Check if already running
    if config["pid_file"].exists():
        print(f"⚠️  {config['name']} appears to be already running")
        return False
    
    # Check if port is in use
    if is_port_in_use(config["port"]):
        print(f"❌ Port {config['port']} is already in use")
        return False
    
    # Start the proxy
    script_path = SCRIPT_DIR / config["script"]
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False
    
    # Make sure script is executable
    script_path.chmod(0o755)
    
    # Start process
    print(f"Starting {config['name']}...")
    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True
    )
    
    # Save PID
    config["pid_file"].write_text(str(process.pid))
    
    # Update environment
    update_env(proxy_type)
    
    print(f"✅ Started {config['name']} (PID: {process.pid})")
    print(f"   URL: {config['env_url']}")
    return True

def update_env(proxy_type):
    """Update .env file with the selected proxy URL."""
    config = PROXY_CONFIGS.get(proxy_type)
    if not config:
        return
    
    env_file = PROJECT_DIR / ".env"
    
    # Read existing env
    env_lines = []
    if env_file.exists():
        env_lines = env_file.read_text().splitlines()
    
    # Update or add ARGO_PROXY_URL
    updated = False
    for i, line in enumerate(env_lines):
        if line.startswith("ARGO_PROXY_URL="):
            env_lines[i] = f"ARGO_PROXY_URL={config['env_url']}"
            updated = True
            break
    
    if not updated:
        env_lines.append(f"ARGO_PROXY_URL={config['env_url']}")
    
    # Write back
    env_file.write_text("\n".join(env_lines) + "\n")
    print(f"   Updated .env with ARGO_PROXY_URL={config['env_url']}")

def status():
    """Show status of all proxies."""
    print("Argo Proxy Status")
    print("=" * 50)
    
    for proxy_type, config in PROXY_CONFIGS.items():
        pid_file = config["pid_file"]
        running = False
        pid = None
        
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                # Check if process is actually running
                os.kill(pid, 0)
                running = True
            except (ProcessLookupError, ValueError):
                # Process not running, clean up
                pid_file.unlink()
        
        # Also check port
        port_in_use = is_port_in_use(config["port"])
        
        status_icon = "🟢" if running else "🔴"
        print(f"\n{status_icon} {config['name']}")
        print(f"   Type: {proxy_type}")
        print(f"   Port: {config['port']} {'(in use)' if port_in_use else ''}")
        print(f"   PID: {pid if running else 'Not running'}")
        print(f"   URL: {config['env_url']}")

def switch(proxy_type):
    """Switch to a different proxy type."""
    print(f"Switching to {proxy_type} proxy...")
    
    # Stop all proxies
    for ptype in PROXY_CONFIGS:
        stop_proxy(ptype)
    
    # Start the requested proxy
    if start_proxy(proxy_type):
        print(f"\n✅ Switched to {PROXY_CONFIGS[proxy_type]['name']}")
        print(f"   BAML clients will now use: {PROXY_CONFIGS[proxy_type]['env_url']}")
    else:
        print(f"\n❌ Failed to switch to {proxy_type}")

def test_proxy():
    """Test the currently configured proxy."""
    env_file = PROJECT_DIR / ".env"
    proxy_url = None
    
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("ARGO_PROXY_URL="):
                proxy_url = line.split("=", 1)[1].strip()
                break
    
    if not proxy_url:
        print("❌ No ARGO_PROXY_URL configured in .env")
        return
    
    print(f"Testing proxy at: {proxy_url}")
    
    # Run test script
    test_script = PROJECT_DIR / "test_argo_direct.py"
    if test_script.exists():
        subprocess.run([sys.executable, str(test_script)])
    else:
        print("❌ Test script not found")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: manage-argo-proxy.py <command> [options]")
        print("\nCommands:")
        print("  start <fixed|custom>  - Start a specific proxy")
        print("  stop <fixed|custom>   - Stop a specific proxy")
        print("  switch <fixed|custom> - Switch to a different proxy")
        print("  status               - Show status of all proxies")
        print("  test                 - Test the current proxy")
        print("\nExamples:")
        print("  manage-argo-proxy.py switch custom")
        print("  manage-argo-proxy.py status")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "status":
        status()
    elif command == "test":
        test_proxy()
    elif command in ["start", "stop", "switch"]:
        if len(sys.argv) < 3:
            print(f"❌ Please specify proxy type: fixed or custom")
            sys.exit(1)
        proxy_type = sys.argv[2].lower()
        if proxy_type not in PROXY_CONFIGS:
            print(f"❌ Unknown proxy type: {proxy_type}")
            print("   Valid types: fixed, custom")
            sys.exit(1)
        
        if command == "start":
            start_proxy(proxy_type)
        elif command == "stop":
            stop_proxy(proxy_type)
        elif command == "switch":
            switch(proxy_type)
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()