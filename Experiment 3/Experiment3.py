import hashlib
import hmac
import secrets
import time

SECRET = "cyber123"
used_nonces = set()


def make_response(nonce, timestamp):
    data = nonce + str(timestamp)
    return hmac.new(
        SECRET.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()


print("=== Authentication System ===")

nonce = secrets.token_hex(4)
timestamp = int(time.time())

print("Nonce:", nonce)

client_response = make_response(nonce, timestamp)

if nonce not in used_nonces and time.time() - timestamp <= 10:
    correct_response = make_response(nonce, timestamp)

    if hmac.compare_digest(client_response, correct_response):
        print("Authentication Successful")
        used_nonces.add(nonce)
else:
    print("Authentication Failed")


print("\n=== Replay Attack Test ===")

old_response = client_response

new_nonce = secrets.token_hex(4)
new_timestamp = int(time.time())

if new_nonce in used_nonces:
    print("Replay Attack Detected")
else:
    new_response = make_response(new_nonce, new_timestamp)

    if hmac.compare_digest(old_response, new_response):
        print("Replay Attack Not Detected")
    else:
        print("Replay Attack Detected")


print("\n=== Timestamp Test ===")

old_time = int(time.time()) - 20
old_nonce = secrets.token_hex(4)
old_response = make_response(old_nonce, old_time)

if time.time() - old_time > 10:
    print("Old Response Rejected")
else:
    print("Response Accepted")
