# scripts/run_myredis.py

#!/usr/bin/env python3
import subprocess
import sys

# docker run -d -p 6379:6379 --name myredis redis:latest
def main():
    # Build the docker run command
    cmd = [
        "docker", "run", "-d",
        "-p", "6379:6379",
        "--name", "myredis",
        "redis:latest"
    ]
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print("Redis container started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running docker: {e}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
