#!/usr/bin/env python3
"""
BeatBridge Backend Launch Script

This script launches the BeatBridge backend service and its dependencies.
"""

import os
import sys
import signal
import subprocess
import time
import argparse
from pathlib import Path

# Define colors for output
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
RESET = "\033[0m"

# Track running processes
processes = []

def signal_handler(sig, frame):
    """Handle termination signals."""
    print(f"\n{YELLOW}Shutting down services...{RESET}")
    for proc in processes:
        if proc.poll() is None:  # Check if process is still running
            proc.terminate()
    sys.exit(0)

def run_command(command, name, env=None):
    """Run a command as a subprocess."""
    try:
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Open log files
        stdout_log = open(f"logs/{name}.log", "a")
        stderr_log = open(f"logs/{name}.err", "a")
        
        # Add timestamp to logs
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        stdout_log.write(f"\n\n--- {name} started at {timestamp} ---\n\n")
        stderr_log.write(f"\n\n--- {name} started at {timestamp} ---\n\n")
        
        # Start process
        print(f"{BLUE}Starting {name}...{RESET}")
        proc = subprocess.Popen(
            command,
            stdout=stdout_log,
            stderr=stderr_log,
            env=env,
            shell=True
        )
        
        # Add to list of processes
        processes.append(proc)
        
        print(f"{GREEN}{name} started (PID: {proc.pid}){RESET}")
        return proc
        
    except Exception as e:
        print(f"{RED}Error starting {name}: {str(e)}{RESET}")
        return None

def check_redis():
    """Check if Redis is running."""
    try:
        import redis
        
        # Get Redis URL from environment or use default
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # Try to connect to Redis
        r = redis.from_url(redis_url)
        r.ping()
        
        print(f"{GREEN}Redis is running.{RESET}")
        return True
        
    except Exception as e:
        print(f"{RED}Redis is not running: {str(e)}{RESET}")
        return False

def setup_environment():
    """Set up the environment for the services."""
    # Load environment variables from .env file
    if Path("../.env").exists():
        print(f"{BLUE}Loading environment variables from ../.env{RESET}")
        with open("../.env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value
    
    # Make sure FLASK_APP is set
    if "FLASK_APP" not in os.environ:
        os.environ["FLASK_APP"] = "service.py"
    
    return dict(os.environ)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Launch BeatBridge backend services")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--no-redis", action="store_true", help="Don't start Redis")
    parser.add_argument("--no-worker", action="store_true", help="Don't start RQ worker")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", default="5001", help="Port to bind to")
    return parser.parse_args()

def main():
    """Main function."""
    # Parse arguments
    args = parse_arguments()
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Set up environment
    env = setup_environment()
    
    # If debug mode, set FLASK_DEBUG
    if args.debug:
        env["FLASK_DEBUG"] = "1"
        env["FLASK_ENV"] = "development"
    
    # Start Redis if needed
    if not args.no_redis:
        # Check if Redis is already running
        if not check_redis():
            print(f"{YELLOW}Starting Redis server...{RESET}")
            redis_proc = run_command("redis-server", "redis")
            if not redis_proc:
                print(f"{RED}Failed to start Redis. Is it installed?{RESET}")
                print(f"{YELLOW}You can install Redis or use --no-redis to skip.{RESET}")
                return
            
            # Give Redis time to start
            time.sleep(2)
    
    # Start RQ worker if needed
    if not args.no_worker:
        print(f"{BLUE}Starting RQ worker...{RESET}")
        worker_proc = run_command(
            "rq worker beatbridge --url redis://localhost:6379/0",
            "rq-worker",
            env=env
        )
    
    # Start Flask application
    print(f"{BLUE}Starting BeatBridge backend service...{RESET}")
    flask_proc = run_command(
        f"gunicorn --bind {args.host}:{args.port} --workers 3 service:app",
        "backend-service",
        env=env
    )
    
    if flask_proc:
        print(f"{GREEN}BeatBridge backend service is running at http://{args.host}:{args.port}{RESET}")
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()