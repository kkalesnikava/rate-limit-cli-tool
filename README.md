# rate-limit-cli-tool

A command-line tool that simulates API rate limiting with a sliding time window. It tracks per-client request counts, enforces configurable limits, and persists state across invocations using a local JSON file.

## Features

- **Sliding 30-second window** — only requests from the last 30 seconds count toward the limit
- **Per-client rate limits** — premium clients get higher limits; all others use the default
- **Persistent state** — request history is saved to `state.json` so limits are enforced across multiple runs
- **Human-readable status** — see usage, time until the next available slot, and whether a client is currently rate-limited
- **No external dependencies** — uses only the Python standard library (`sys`, `time`, `json`, `os`, `collections`)

## Requirements

- Python 3.6 or later

## Usage

```
python3 tool.py <command> [clientid]
```

### Commands

| Command | Arguments | Description |
|---|---|---|
| `request` | `<clientid>` | Simulate an API request for a client. Returns `200 OK` or `429 Too Many Requests`. |
| `status` | `<clientid>` | Show the current rate limit status for a client. |
| `list` | — | List all clients that have recent activity. |
| `clear` | — | Delete all saved state (useful for testing). |
| `help` | — | Display the help message. |

Client names are **case-insensitive** (automatically converted to lowercase).

## Rate Limits

| Client type | Limit |
|---|---|
| Default (any client) | 5 requests / 30 s |
| `john` (premium) | 10 requests / 30 s |
| `terry` (premium) | 15 requests / 30 s |
| `michael` (premium) | 20 requests / 30 s |
| `eric` (premium) | 30 requests / 30 s |

## Examples

### Make a request

```
$ python3 tool.py request john
200 OK (1/10 requests in window)

$ python3 tool.py request john
200 OK (2/10 requests in window)
```

Once the limit is reached:

```
$ python3 tool.py request john
429 Too Many Requests (limit: 10/30s)
```

### Check status for a client

```
$ python3 tool.py status john
Client: john
Rate Limit: 10 per 30s
Requests in window: 10/10
Newest request age: 2.3s
Time till next slot: 27.7s
Rate Limited: YES
```

### List all active clients

```
$ python3 tool.py list
john: 10/10 requests
alice: 3/5 requests
```

### Clear state

```
$ python3 tool.py clear
State cleared
```

## State File

Request timestamps are persisted in `state.json` in the current working directory. The file is created automatically on the first request and can be removed with the `clear` command or by deleting it manually. At most 100 timestamps are stored per client to prevent unbounded memory growth.

## Running the Test Script

A shell script is included to demonstrate the rate limiting behaviour. It clears existing state, sends 15 requests for the premium client `john` (limit: 10/30 s) with a 0.5 s delay between each, then prints the status and client list.

```
bash test.sh
```