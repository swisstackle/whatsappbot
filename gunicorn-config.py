import os
# Bind to the port provided by the platform (fallback to 8080 for local dev)
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = 2
