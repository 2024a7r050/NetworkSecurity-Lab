from hashlib import sha256
import os
import json
import time


def generate_hash(path):
    with open(path, "rb") as f:
        return sha256(f.read()).hexdigest()


folder = input("Enter folder name: ")

# Create original hashes
original_hashes = {}

for file in os.listdir(folder):
    path = os.path.join(folder, file)

    if os.path.isfile(path):
        original_hashes[file] = generate_hash(path)

print("\nOriginal hashes created.")
print("File Integrity Monitoring started...")
print("Checking every 4 seconds.")
print("Press Ctrl+C to stop.\n")

# Store the state from the first check
previous_hashes = original_hashes.copy()


try:
    while True:

        current_hashes = {}

        for file in os.listdir(folder):
            path = os.path.join(folder, file)

            if os.path.isfile(path):
                current_hashes[file] = generate_hash(path)

        # Check existing files
        for file in original_hashes:

            if file not in current_hashes:
                if file in previous_hashes:
                    print("ALERT:", file, "has been DELETED.")

            else:
                # File changed from previous check
                if file in previous_hashes:
                    if previous_hashes[file] != current_hashes[file]:

                        # Check whether it returned to original
                        if current_hashes[file] == original_hashes[file]:
                            print("RESTORED:", file,
                                  "has been restored to its original state.")

                        else:
                            print("ALERT:", file, "has been MODIFIED.")

        # Check for new files
        for file in current_hashes:
            if file not in previous_hashes:
                print("ALERT:", file, "is a NEW file.")

        # Update previous state
        previous_hashes = current_hashes.copy()

        time.sleep(4)


except KeyboardInterrupt:
    print("\nMonitoring stopped.")
