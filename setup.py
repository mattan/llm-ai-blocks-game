#!/usr/bin/env python3
"""
Setup script for the Flask application on PythonAnywhere.
This script will:
1. Pull the latest changes from Git
2. Install or update dependencies
3. Touch the WSGI file to restart the application
"""

import os
import subprocess
import sys


def run_command(command):
    """Run a shell command and print output."""
    print(f"Running: {command}")
    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True
        )
        print(output)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.output}")
        return False


def setup_app():
    """Setup the application."""
    # Get the current directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    
    # Pull latest changes from git
    if not run_command("git pull"):
        if not run_command("git status"):
            print("No git repository found. Cloning repository first...")
            # This assumes you have set up your Git repository on PythonAnywhere
            repo_url = os.environ.get("GIT_REPO_URL", "https://github.com/your-username/your-repo.git")
            if not run_command(f"git clone {repo_url} ."):
                print("Failed to clone repository.")
                sys.exit(1)
    
    # Install or update dependencies
    if not run_command("pip install -r requirements.txt"):
        print("Failed to install dependencies.")
        sys.exit(1)
    
    # Touch the WSGI file to restart the application
    wsgi_file = os.path.join(app_dir, "wsgi.py")
    if os.path.exists(wsgi_file):
        if run_command(f"touch {wsgi_file}"):
            print("Application restarted successfully.")
        else:
            print("Failed to restart the application.")
    else:
        print("WSGI file not found. Application not restarted.")


if __name__ == "__main__":
    setup_app() 