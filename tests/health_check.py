import subprocess
import json
import urllib.request
import urllib.error

def get_container_status():
    """Get the status of all nebulax containers."""
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        containers = []
        if output:
            for line in output.split('\n'):
                try:
                    containers.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return containers
    except subprocess.CalledProcessError as e:
        print(f"Error running docker compose ps: {e}")
        return []

def check_endpoint(name, url):
    """Check if an HTTP endpoint is up."""
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if response.status < 500:
                return True, f"Status {response.status}"
            else:
                return False, f"Status {response.status}"
    except urllib.error.HTTPError as e:
        # HTTPError is raised for 4xx/5xx, but 4xx means the server is up
        if e.code < 500:
             return True, f"Status {e.code}"
        return False, f"Status {e.code}"
    except urllib.error.URLError as e:
        return False, f"Connection Failed: {e.reason}"
    except Exception as e:
        return False, str(e)

def main():
    print("--- NebulaX System Health Check ---")
    
    # 1. Check Infrastructure (Docker)
    print("\n[1] Checking Infrastructure (Docker)...")
    containers = get_container_status()
    
    infra_services = ["nebulax-db", "nebulax-bus"]
    infra_status = {name: "Not Found" for name in infra_services}

    if containers:
        for c in containers:
            name = c.get('Name', c.get('Service', 'Unknown'))
            state = c.get('State', 'Unknown')
            # Check if this container matches one of our infra services
            for infra in infra_services:
                if infra in name:
                    infra_status[infra] = state

    for name, status in infra_status.items():
        if status.lower() == "running":
            print(f"✅ {name}: {status}")
        else:
            print(f"❌ {name}: {status}")

    # 2. Check Services (Endpoints)
    print("\n[2] Checking Service Endpoints...")
    endpoints = [
        ("Core API", "http://localhost:8000/docs"),
        ("Dashboard", "http://localhost:3000"),
        ("Ground Sim", "http://localhost:5001"),
        ("Target Web", "http://localhost:8080"),
    ]

    all_endpoints_up = True
    for name, url in endpoints:
        success, msg = check_endpoint(name, url)
        if success:
            print(f"✅ {name}: Up ({msg})")
        else:
            print(f"❌ {name}: Down ({msg})")
            all_endpoints_up = False

    print("\n--- Summary ---")
    if all_endpoints_up:
        print("System Core is responsive.")
    else:
        print("Some core services are not reachable.")

if __name__ == "__main__":
    main()
