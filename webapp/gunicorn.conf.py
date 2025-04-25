"""Gunicorn configuration file for BeatBridge webapp"""

# Bind to 0.0.0.0:5000
bind = "0.0.0.0:5000"

# Number of worker processes
workers = 3

# Number of threads per worker
threads = 2

# Maximum number of pending connections
backlog = 2048

# Timeout in seconds for a request to complete
timeout = 60

# Restart workers after this many requests
max_requests = 1000

# Restart workers after this many seconds
max_requests_jitter = 50

# Log level
loglevel = "info"

# Access log format
accesslog = "-"  # stdout
errorlog = "-"   # stderr

# Process name
proc_name = "beatbridge_webapp"

# Preload the application code before worker processes are forked
preload_app = True

# Worker class
worker_class = "sync"

# Automatically restart workers that have used more than this amount of memory
worker_tmp_dir = "/dev/shm"