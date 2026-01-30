import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', 5000)}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

errorlog = "-"
accesslog = "-"
loglevel = "info"

preload_app = True
daemon = False
