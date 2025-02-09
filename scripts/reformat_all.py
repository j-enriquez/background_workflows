"""
Simple script to reformat all .py files in the project using Black.
"""

import subprocess
import sys
import os


def main():
    # Default to current directory if no argument is provided:
    target_directory = "../"

    # Run black on that directory
    try:
        subprocess.run(["black", target_directory], check=True)
    except FileNotFoundError:
        print("Error: Black not installed or not on PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Black formatting failed: {e}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
