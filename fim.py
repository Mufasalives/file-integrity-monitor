import hashlib
import json
import os
import time
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Replace with your actual Discord or Slack webhook URL
WEBHOOK_URL = "YOUR_DISCORD_OR_SLACK_WEBHOOK_URL"

def calculate_file_hash(file_path):
    """Calculate and return the SHA-256 hash of the file."""
    hash_object = hashlib.sha256()
    with open(file_path, 'rb') as file:
        file_data = file.read()
        hash_object.update(file_data)
    return hash_object.hexdigest()

def send_alert(file_path, old_hash, new_hash):
    """Send real-time alert to Slack or Discord webhook."""
    if not WEBHOOK_URL or "YOUR_DISCORD" in WEBHOOK_URL:
        return  # Skip sending if webhook URL isn't configured
    
    payload = {
        "content": f"🚨 **SECURITY ALERT**: Unauthorized change detected in `{file_path}`!\nOld Hash: `{old_hash[:10]}...`\nNew Hash: `{new_hash[:10]}...`"
    }
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Failed to send webhook alert: {e}")

def log_change(file_path, old_hash, new_hash):
    """Log the structured JSON change event to the log file."""
    log_directory = os.path.join(BASE_DIR, "logs")
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file_path = os.path.join(log_directory, "file_changes.log")

    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event_type": "FILE_MODIFIED",
        "file_path": file_path,
        "previous_hash": old_hash,
        "current_hash": new_hash,
        "hash_algorithm": "SHA-256"
    }

    with open(log_file_path, "a") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")

files_to_monitor = [
    os.path.join(BASE_DIR, ".watched_file.txt")
]

def monitor_files():
    """Monitor files for changes by comparing their hashes."""
    previous_hashes = {}

    while True:
        for file_path in files_to_monitor:
            if os.path.exists(file_path):
                current_hash = calculate_file_hash(file_path)

                if file_path not in previous_hashes:
                    previous_hashes[file_path] = current_hash
                    print(f"Baseline created for: {file_path}")

                elif previous_hashes[file_path] != current_hash:
                    old_hash = previous_hashes[file_path]
                    print(f"[WARNING]: File has changed: {file_path}")
                    
                    send_alert(file_path, old_hash, current_hash)
                    log_change(file_path, old_hash, current_hash)
                    
                    previous_hashes[file_path] = current_hash

                else:
                    print(f"No change detected for: {file_path}")

            else:
                print(f"File does not exist: {file_path}")

        time.sleep(5)

if __name__ == "__main__":
    monitor_files()