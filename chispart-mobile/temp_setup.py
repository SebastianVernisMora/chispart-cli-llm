from core.api_key_manager import APIKeyManager

print("Starting non-interactive setup...")
# We need to instantiate the manager, not use the global one, to control the path
# But for this script, the global one should be fine as it will use the default path
from core.api_key_manager import api_key_manager

api_key_manager.set_api_key("blackbox", "dummy_key_for_testing")
print("Dummy API key for blackbox has been set.")
print("Setup complete.")
