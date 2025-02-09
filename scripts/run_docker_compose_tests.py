# scripts/run_tests.py

#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Run docker-compose to build and run tests."
    )
    parser.add_argument(
        "--detached",
        action="store_true",
        help="Run containers in detached mode (background)."
    )
    args = parser.parse_args()

    # Change to the directory that contains your docker-compose.yml.
    # Adjust this path if needed.
    docker_dir = os.path.join(os.path.dirname(__file__), "../docker")
    if not os.path.isdir(docker_dir):
        print(f"Error: Directory '{docker_dir}' does not exist.")
        sys.exit(1)

    os.chdir(docker_dir)
    print("Starting docker-compose with --build...")

    # Build the docker-compose command
    cmd = ["docker-compose", "up", "--build"]
    if args.detached:
        cmd.append("-d")

    # Run the command
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"docker-compose failed with return code {e.returncode}")
        sys.exit(e.returncode)

    if args.detached:
        print(
            "Containers are running in detached mode.\n"
            "Use 'docker-compose logs' or 'docker-compose down' when ready."
        )

if __name__ == "__main__":
    main()
