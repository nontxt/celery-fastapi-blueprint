# flowerconfig.py
from celery import Celery

# Security settings (e.g., basic authentication)
basic_auth = "admin:admin"

# Celery Broker URL (configured to Redis)
# broker_api = 'redis://redis:6379/0'

# Enable monitoring of tasks (status updates every second)
state_update_interval = 1  # in seconds

# Celery configuration
# broker = 'redis://redis:6379/0'

# URL for logging and authentication (Optional)
# url_prefix = 'flower'  # Access Flower through http://localhost:5555/flower

# Flower specific configurations
port = 5555
