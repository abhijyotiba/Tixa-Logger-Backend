"""
API Key Generator
Generates cryptographically secure API keys for clients
"""
import secrets
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_api_key():
    """
    Generate a cryptographically secure API key
    Uses URL-safe base64 encoding with 32 bytes of randomness
    """
    return secrets.token_urlsafe(32)


def load_existing_keys():
    """Load existing API keys from .env file"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    if not os.path.exists(env_path):
        return {}
    
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('API_KEYS='):
                keys_str = line.split('=', 1)[1].strip()
                try:
                    return json.loads(keys_str.replace("'", '"'))
                except:
                    return {}
    return {}


def save_keys_to_env(keys_dict):
    """Update API_KEYS in .env file"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    # Read existing .env
    lines = []
    found = False
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    
    # Update or add API_KEYS line
    keys_json = json.dumps(keys_dict)
    new_line = f'API_KEYS={keys_json}\n'
    
    for i, line in enumerate(lines):
        if line.startswith('API_KEYS='):
            lines[i] = new_line
            found = True
            break
    
    if not found:
        lines.append(new_line)
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print(f"\n✅ Updated {env_path}")


def main():
    print("=" * 70)
    print(" " * 20 + "API Key Generator")
    print("=" * 70)
    
    # Get client details
    print("\nEnter client information:")
    client_id = input("  Client ID (e.g., 'acme_corp'): ").strip()
    
    if not client_id:
        print("\n❌ Error: client_id is required")
        return
    
    # Optional: client name for reference
    client_name = input("  Client Name (optional): ").strip()
    
    # Generate key
    api_key = generate_api_key()
    
    # Load existing keys
    existing_keys = load_existing_keys()
    
    # Check for duplicate client_id
    if client_id in existing_keys.values():
        print(f"\n⚠️  Warning: client_id '{client_id}' already exists")
        overwrite = input("  Generate new key for this client? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Cancelled.")
            return
        
        # Remove old key for this client
        existing_keys = {k: v for k, v in existing_keys.items() if v != client_id}
    
    # Add new key
    existing_keys[api_key] = client_id
    
    # Display results
    print("\n" + "=" * 70)
    print("✅ API Key Generated Successfully!")
    print("=" * 70)
    print(f"\nClient ID:   {client_id}")
    if client_name:
        print(f"Client Name: {client_name}")
    print(f"API Key:     {api_key}")
    print("\n" + "=" * 70)
    print("⚠️  IMPORTANT: Save this information securely!")
    print("=" * 70)
    
    # Show .env format
    print("\n📝 Your updated .env configuration:")
    print("-" * 70)
    print(f"API_KEYS={json.dumps(existing_keys, indent=2)}")
    print("-" * 70)
    
    # Ask to save
    save = input("\n💾 Automatically update .env file? (y/N): ").strip().lower()
    if save == 'y':
        save_keys_to_env(existing_keys)
        print("\n⚠️  Remember to restart your server for changes to take effect!")
    else:
        print("\n📋 Copy the API_KEYS value above to your .env file manually")
    
    # Client instructions
    print("\n" + "=" * 70)
    print("📧 Send this to your client:")
    print("=" * 70)
    print("\nLogger API Configuration:")
    print("-" * 70)
    print("Endpoint:    https://your-logger-api.com/api/v1/logs")
    print(f"API Key:     {api_key}")
    print("Header Name: X-API-Key")
    print("\nExample Usage:")
    print("  curl -X POST https://your-logger-api.com/api/v1/logs \\")
    print(f"    -H 'X-API-Key: {api_key}' \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{...}'")
    print("-" * 70)
    
    # Save to file option
    save_file = input("\n💾 Save client instructions to file? (y/N): ").strip().lower()
    if save_file == 'y':
        filename = f"client_instructions_{client_id}.txt"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w') as f:
            f.write(f"Logger API Credentials\n")
            f.write(f"Generated: {__import__('datetime').datetime.now().isoformat()}\n")
            f.write(f"=" * 70 + "\n\n")
            f.write(f"Client ID:   {client_id}\n")
            if client_name:
                f.write(f"Client Name: {client_name}\n")
            f.write(f"\nEndpoint:    https://your-logger-api.com/api/v1/logs\n")
            f.write(f"API Key:     {api_key}\n")
            f.write(f"Header Name: X-API-Key\n\n")
            f.write("Setup Instructions:\n")
            f.write("1. Add to your .env file:\n")
            f.write(f"   LOGGER_API_URL=https://your-logger-api.com/api/v1/logs\n")
            f.write(f"   LOGGER_API_KEY={api_key}\n\n")
            f.write("2. Never commit .env to version control\n\n")
            f.write("3. Use in your code:\n")
            f.write("   headers = {'X-API-Key': os.getenv('LOGGER_API_KEY')}\n")
            f.write("   requests.post(url, headers=headers, json=log_data)\n")
        
        print(f"\n✅ Saved to: {filepath}")
    
    print("\n" + "=" * 70)
    print("✅ Done!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
