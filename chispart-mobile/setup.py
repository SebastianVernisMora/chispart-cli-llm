"""
Chispart Mobile - Interactive Setup Script
Guides the user through initial configuration.
"""

import asyncio
import os
from getpass import getpass

from core.api_key_manager import api_key_manager
from core.config_manager import config_manager


async def main():
    """Main setup function."""
    print("🚀 Welcome to Chispart Mobile Setup!")
    print("This script will help you configure your API keys.")
    print("-" * 40)

    # --- Configure Blackbox (required) ---
    print("\n1. Blackbox AI API Key (Required)")
    print("   You can get your key from: https://www.blackbox.ai/api-keys")

    while True:
        blackbox_key = getpass("   Enter your Blackbox API Key: ")
        if not blackbox_key.strip():
            print("   ❌ API Key cannot be empty. Please try again.")
            continue

        print("   Validating key...")
        api_key_manager.set_api_key("blackbox", blackbox_key)
        validation = await api_key_manager.validate_api_key(
            "blackbox", force_refresh=True
        )

        if validation.get("valid"):
            print("   ✅ Blackbox API Key is valid and saved securely.")
            break
        else:
            print(
                f"   ❌ Validation failed: {validation.get('error', 'Unknown error')}"
            )
            print("   Please check your key and try again.")
            api_key_manager.remove_api_key("blackbox")

    # --- Configure other providers (optional) ---
    print("\n2. Optional API Keys")
    print("   You can add keys for other providers now or later via the web UI.")

    other_providers = ["openai", "anthropic", "groq", "together"]
    for provider in other_providers:
        key = getpass(f"   Enter {provider.title()} API Key (or press Enter to skip): ")
        if key.strip():
            api_key_manager.set_api_key(provider, key)
            print(f"   ✅ {provider.title()} API Key saved.")

    # --- Final Configuration ---
    config_manager.set("default_api", "blackbox")
    config_manager.set(
        "default_model", "blackbox-ai/gpt-4o"
    )  # A sensible default for Blackbox

    print("-" * 40)
    print("🎉 Setup Complete!")
    print("You can now start the application by running:")
    if os.environ.get("PREFIX") and "com.termux" in os.environ.get("PREFIX"):
        print("   ./start-termux.sh")
    else:
        print("   ./start.sh")


if __name__ == "__main__":
    asyncio.run(main())
