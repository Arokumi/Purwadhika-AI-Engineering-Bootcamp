# KEYS
AVN_PASSWORD = None
QDRANT_API_KEY = None
QDRANT_URL = None
OPENAI_API_KEY = None

# CERTIFICATE PATH
CERTIFICATE_PATH = None

def update_keys(avn_pass, qdrant_key, qdrant_url, openai_key):
    AVN_PASSWORD = avn_pass
    QDRANT_API_KEY = qdrant_key
    QDRANT_URL = qdrant_url
    OPENAI_API_KEY = openai_key

def update_path(path):
    CERTIFICATE_PATH = path