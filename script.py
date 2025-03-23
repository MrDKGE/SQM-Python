import os
import sys
import time
import json
import requests
import datetime
from collections import defaultdict


# ANSI color codes for colored output.
def print_info(message):
    print("\033[94m" + message + "\033[0m")


def print_error(message):
    print("\033[91m" + message + "\033[0m")


def print_block(message):
    separator = "\033[93m" + ("-" * 40) + "\033[0m"
    print(separator)
    print("\033[93m" + message + "\033[0m")
    print(separator)


# Configurable patterns for detecting stalled downloads.
STALLED_ERROR_PATTERNS = [
    "The download is stalled with no connections",
    "is downloading metadata"
]

STALLED_STATUS_PATTERNS = [
    "Sample",
    "No files found are eligible for import in"
]

# File to persist stalled downloads when using delayed removal.
STALLED_DOWNLOADS_FILE = 'stalled_downloads.json'


def load_stalled_downloads_by_server(filename=STALLED_DOWNLOADS_FILE):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print_error(f"Failed to load stalled downloads from {filename}: {e}")
    return {}


def load_stalled_downloads_for_server(server_name, filename=STALLED_DOWNLOADS_FILE):
    data = load_stalled_downloads_by_server(filename)
    return set(data.get(server_name, []))


def save_stalled_downloads_for_server(server_name, stalled_set, filename=STALLED_DOWNLOADS_FILE):
    data = load_stalled_downloads_by_server(filename)
    data[server_name] = list(stalled_set)
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print_error(f"Failed to save stalled downloads to {filename}: {e}")


def load_config():
    config_file = 'config.json'
    if not os.path.exists(config_file):
        print_error(f"Config file {config_file} not found. Provide a valid config.json file.")
        sys.exit(1)
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            print_info("Configuration loaded from config.json")
            return validate_config(config)
    except (json.JSONDecodeError, Exception) as e:
        print_error(f"Error reading {config_file}: {e}")
        sys.exit(1)


def validate_config(config):
    required_global = ["interval", "dry_run", "log_level", "servers"]
    required_server = ["api_key", "host", "port", "protocol", "skip_redownload", "name"]

    for field in required_global:
        if field not in config:
            print_error(f"Missing global configuration field: {field}")
            sys.exit(1)

    if not isinstance(config.get("servers"), list) or not config["servers"]:
        print_error("The 'servers' configuration must be a non-empty list.")
        sys.exit(1)

    server_names = [server.get("name") for server in config["servers"]]
    if len(set(server_names)) != len(server_names):
        print_error("All server names must be unique in the configuration.")
        sys.exit(1)

    try:
        config["interval"] = int(config["interval"])
        config["dry_run"] = bool(config["dry_run"])
        if not isinstance(config["log_level"], str):
            raise ValueError("log_level must be a string")
    except (ValueError, TypeError) as e:
        print_error(f"Global configuration error: {e}")
        sys.exit(1)

    config["stalled_policy"] = config.get("stalled_policy", "immediate")
    if config["stalled_policy"] not in ["immediate", "delayed"]:
        print_error("Invalid stalled_policy in config. Must be either 'immediate' or 'delayed'.")
        sys.exit(1)

    for index, server in enumerate(config["servers"]):
        if "name" not in server:
            print_error(f"Server at index {index} lacks a 'name'.")
            sys.exit(1)
        for field in required_server:
            if field not in server:
                print_error(f"Server '{server.get('name', 'unknown')}' missing field: {field}")
                sys.exit(1)
        try:
            server["skip_redownload"] = bool(server["skip_redownload"])
            server["port"] = str(server["port"])
        except (ValueError, TypeError) as e:
            print_error(f"Error in server '{server['name']}' configuration: {e}")
            sys.exit(1)

    return config


def api_call(base_url, endpoint, api_key, method='GET', params=None, payload=None):
    url = f"{base_url}{endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': api_key
    }
    try:
        response = requests.request(method, url, headers=headers, params=params, json=payload, timeout=30)
        if response.status_code in (401, 404):
            error_msg = "Authentication failed" if response.status_code == 401 else "Resource not found"
            print_error(f"{error_msg} for {url}")
            return None
        response.raise_for_status()
        if not response.text:
            return None
        return response.json()
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException) as err:
        print_error(f"Error with request {url}: {err}")
    except Exception as err:
        print_error(f"Unexpected error with {url}: {err}")
    return None


def refresh_queue(base_url, api_key):
    response = api_call(
        base_url, "command", api_key, method='POST',
        payload={"name": "RefreshMonitoredDownloads"}
    )
    if response and response.get('status') in ['started', 'queued']:
        print_info("Queue refresh initiated successfully.")
        time.sleep(5)
        return True
    print_error("Queue refresh initiation failed.")
    return False


def is_download_stalled(record):
    error_message = record.get('errorMessage', '')
    for pattern in STALLED_ERROR_PATTERNS:
        if pattern in error_message:
            return True
    for msg in record.get('statusMessages', []):
        for pattern in STALLED_STATUS_PATTERNS:
            if pattern in msg.get('title', ''):
                return True
            for sub_msg in msg.get('messages', []):
                if pattern in str(sub_msg):
                    return True
    return False


def get_stalled_ids(records):
    no_download_id_records = []
    download_groups = defaultdict(list)
    for record in records:
        download_id = record.get('downloadId')
        if download_id:
            download_groups[download_id].append(record)
        else:
            no_download_id_records.append(record)
    stalled_ids = []
    for download_id, group in download_groups.items():
        for record in group:
            if is_download_stalled(record):
                if len(group) > 1:
                    print_info(f"Season pack detected with {len(group)} episodes. Using episode ID: {record['id']}")
                stalled_ids.append(record['id'])
                break
    for record in no_download_id_records:
        if is_download_stalled(record):
            stalled_ids.append(record['id'])
    return stalled_ids


def process_queue(base_url, api_key, skip_redownload, dry_run, stalled_policy, server_name):
    queue_info = api_call(
        base_url, 'queue', api_key,
        params={'page': 1, 'pageSize': 250, 'includeUnknownSeriesItems': True}
    )
    if not queue_info:
        print_error("Failed to retrieve queue data.")
        return

    records = queue_info.get('records', [])
    if not records:
        print_info("Queue is empty.")
        if stalled_policy == "delayed":
            save_stalled_downloads_for_server(server_name, set())
        return

    current_stalled_ids = set(get_stalled_ids(records))
    if stalled_policy == "delayed":
        previous_stalled_ids = load_stalled_downloads_for_server(server_name)
        ids_to_remove = current_stalled_ids.intersection(previous_stalled_ids)
        stalled_for_next_pass = current_stalled_ids - ids_to_remove
        save_stalled_downloads_for_server(server_name, stalled_for_next_pass)

        if not ids_to_remove:
            if current_stalled_ids:
                print_block(
                    f"Stalled downloads detected for {server_name}:\n{list(current_stalled_ids)}\nThey have been recorded and will be removed if they remain stalled on the next scan."
                )
            return
        else:
            if dry_run:
                print_block(f"[DRY RUN] Stalled downloads confirmed for removal on {server_name}:\n{list(ids_to_remove)}\nNo changes will be made.")
                return
            else:
                print_block(f"Stalled downloads confirmed for removal on {server_name}:\n{list(ids_to_remove)}")
                stalled_ids = list(ids_to_remove)
    else:
        stalled_ids = list(current_stalled_ids)
        save_stalled_downloads_for_server(server_name, set())
        if dry_run:
            print_block(f"[DRY RUN] Would remove {len(stalled_ids)} stalled record(s) for {server_name}:\n{stalled_ids}\nNo changes will be made.")
            return

    if not stalled_ids:
        print_info("No stalled downloads detected.")
        return

    success = api_call(
        base_url,
        'queue/bulk',
        api_key,
        method='DELETE',
        params={
            'removeFromClient': True,
            'blocklist': True,
            'skipRedownload': skip_redownload,
            'changeCategory': False
        },
        payload={"ids": stalled_ids}
    )

    if success:
        print_block(f"Removed {len(stalled_ids)} stalled record(s) for {server_name}.")
    else:
        print_error("Failed to remove stalled records.")


def process_server(server, dry_run, stalled_policy):
    print_block(f"Processing server: {server['name']}\nRefreshing downloads for {server['name']}...")
    base_url = f"{server['protocol']}://{server['host']}:{server['port']}/api/v3/"
    if refresh_queue(base_url, server['api_key']):
        process_queue(base_url, server['api_key'], server['skip_redownload'], dry_run, stalled_policy, server['name'])
    else:
        print_error(f"Download refresh failed for {server['name']}")


def main(config):
    print_info(f"Loaded configuration for {len(config['servers'])} server(s).")
    stalled_policy = config.get("stalled_policy", "immediate")
    if stalled_policy == "immediate":
        policy_message = "Downloads will be removed immediately upon detection."
    else:
        policy_message = "Downloads will only be removed if they remain stalled on consecutive scans."
    print_block(f"Stalled Download Removal Policy in Use: {stalled_policy.upper()} REMOVAL\n{policy_message}")

    if config.get("dry_run"):
        print_info("Dry Run mode is enabled. No changes will be made.")

    try:
        while True:
            for server in config['servers']:
                try:
                    process_server(server, config['dry_run'], stalled_policy)
                except Exception as e:
                    print_error(f"Error processing server {server['name']}: {e}")
            if config['interval'] <= 0:
                print_info("Interval is 0 or negative. Exiting after a single run.")
                break
            next_scan = datetime.datetime.now() + datetime.timedelta(seconds=config['interval'])
            print_info(f"Next scan will run at: {next_scan.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(config['interval'])
    except KeyboardInterrupt:
        print_info("User interruption detected. Exiting.")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
    return 0


if __name__ == "__main__":
    config = load_config()
    main(config)
