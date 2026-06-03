"""M1 Test: Start server and curl /health endpoint."""
import subprocess
import sys
import time
import urllib.request
import signal
import os
import json

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def test():
    print("=== M1: Project Skeleton Test ===")
    
    # Start server in background
    python = os.path.join(PROJECT_DIR, ".venv", "Scripts", "python.exe")
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_DIR
    
    server = subprocess.Popen(
        [python, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8765"],
        cwd=PROJECT_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    time.sleep(2)
    
    try:
        # Test /health endpoint
        req = urllib.request.Request("http://127.0.0.1:8765/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            print(f"Response: {data}")
            assert data["status"] == "ok", f"Expected status=ok, got {data['status']}"
            assert data["version"] == "0.1.0", f"Expected version=0.1.0, got {data['version']}"
        print("PASS: /health endpoint works!")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    finally:
        server.terminate()
        server.wait()
    
    print("=== M1: All tests passed! ===")

if __name__ == "__main__":
    test()
