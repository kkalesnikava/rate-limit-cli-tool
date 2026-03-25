#!/usr/bin/env python3
"""
Rate Limit CLI
"""

import sys
import time
import json
import os
from collections import deque

PREMIUM_CLIENTS = {"john": 10, "terry": 15, "michael": 20, "eric": 30}
DEFAULT_REQUEST_LIMIT = 5
DEFAULT_WINDOW = 30
STATE_FILE = "state.json"
MAX_STATE_LENGHT = 100


def load_state():
    """Load request state from a JSON file"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                state = {}
                for client, timestamps in data.items():
                    # Prevent unlimited growth
                    state[client] = deque(timestamps, maxlen=MAX_STATE_LENGHT)
                return state
        except (json.JSONDecodeError, KeyError):
            return {}
    return {}


def save_state(state):
    """Save request state to a JSON file"""
    data = {}
    for client, timestamps in state.items():
        data[client] = list(timestamps)
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f)



def get_limit(client):
    """Get rate limit for a client"""
    return PREMIUM_CLIENTS.get(client.lower(), DEFAULT_REQUEST_LIMIT)


def cleanup_old_requests(client, now, requests):
    """Remove requests older than window"""
    if client in requests:
        # Remove timestamps older than DEFAULT_WINDOW seconds
        while requests[client] and (now - requests[client][0] > DEFAULT_WINDOW):
            requests[client].popleft()


def verify_client(client, requests):
    """Ensure client exists in requests dict"""
    if client not in requests:
        requests[client] = deque(maxlen=MAX_STATE_LENGHT)


def request(client_id):
    """Simulate API request with rate limiting"""
    now = time.time()
    client = client_id.lower()

    requests = load_state()
    verify_client(client, requests)
    cleanup_old_requests(client, now, requests)
    used = len(requests[client])
    limit = get_limit(client)

    if used >= limit:
        print(f"429 Too Many Requests (limit: {limit}/30s)")
        save_state(requests)
        return

    requests[client].append(now)
    print(f"200 OK ({used+1}/{limit} requests in window)")
    save_state(requests)


def status(client_id):
    """Show current rate limit status for client"""
    now = time.time()
    client = client_id.lower()

    requests = load_state()
    verify_client(client, requests)
    cleanup_old_requests(client, now, requests)
    used = len(requests[client])
    limit = get_limit(client)

    newest_age = now - requests[client][-1] if used > 0 else DEFAULT_WINDOW
    time_left = max(0, DEFAULT_WINDOW - newest_age) if used > 0 else 0
    limited = used >= limit

    print(f"Client: {client_id}")
    print(f"Rate Limit: {limit} per 30s")
    print(f"Requests in window: {used}/{limit}")
    print(f"Newest request age: {newest_age:.1f}s")
    print(f"Time till next slot: {time_left:.1f}s")
    print(f"Rate Limited: {'YES' if limited else 'NO'}")

    save_state(requests)


def list_clients():
    """List all clients with recent activity"""
    requests = load_state()
    if not requests:
        print("No active clients")
        return

    now = time.time()
    for client in sorted(requests.keys()):
        cleanup_old_requests(client, now, requests)
        used = len(requests[client])
        limit = get_limit(client)
        print(f"{client}: {used}/{limit} requests")

    save_state(requests)


def clear_state():
    """Clear all rate limit state (for testing)"""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    print("State cleared")


def help():
    """Display help message"""
    print("Rate Limit Simulator CLI")
    print("Usage:")
    print("  python cli.py request <clientid>   - Make a simulated API request")
    print("  python cli.py status <clientid>    - Show client's rate limit status")
    print("  python cli.py list                 - List all known clients")
    print("  python cli.py clear                - Clear rate limit state")
    print("  python cli.py help                 - Show this help")
    print("\nPremium clients (case-insensitive): john, terry, michael, eric")
    print(
        f"Default limit: {DEFAULT_REQUEST_LIMIT} requests per {DEFAULT_WINDOW} seconds")
    print(f"State file: {STATE_FILE}")


def main():
    if len(sys.argv) < 2:
        help()
        return

    cmd = sys.argv[1].lower()

    if cmd == "request":
        if len(sys.argv) != 3:
            print("Error: clientid required")
            help()
            return
        request(sys.argv[2])

    elif cmd == "status":
        if len(sys.argv) != 3:
            print("Error: clientid required")
            help()
            return
        status(sys.argv[2])

    elif cmd == "list":
        list_clients()

    elif cmd == "clear":
        clear_state()

    elif cmd == "help":
        help()

    else:
        print(f"Error: Unknown command '{cmd}'")
        help()


if __name__ == "__main__":
    main()
