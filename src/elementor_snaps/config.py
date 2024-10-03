# Default configuration
DEFAULT_CONFIG = {
    "query_selector": '[data-element_type="container"]'
}

# User configuration (can be modified)
user_config = DEFAULT_CONFIG.copy()

def get_config(key):
    return user_config.get(key, DEFAULT_CONFIG.get(key))

def set_config(key, value):
    user_config[key] = value
