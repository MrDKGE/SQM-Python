import logging
import os
import time

import requests

# Constants for defaults
DEFAULTS = {
    "HOST": "127.0.0.1",
    "PORT": "8989",
    "PROTOCOL": "http",
    "INTERVAL": 3600,
    "LOG_LEVEL": "INFO",
    "SKIP_REDOWNLOAD": False,
    "DRY_RUN": False
}

# Initialize a Session
session = requests.Session()


def initialize_logging(log_level):
    logging.basicConfig(
        level=log_level.upper(),
        format='%(levelname)s - %(message)s'
    )


def fetch_env_vars():
    api_key = os.getenv('API_KEY')
    if not api_key:
        logging.error("Missing required environment variable API_KEY. Exiting.")
        exit(1)

    env_vars = {
        "API_KEY": api_key,
        "HOST": os.getenv('HOST', DEFAULTS["HOST"]),
        "PORT": os.getenv('PORT', DEFAULTS["PORT"]),
        "PROTOCOL": os.getenv('PROTOCOL', DEFAULTS["PROTOCOL"]),
        "INTERVAL": int(os.getenv('INTERVAL', DEFAULTS["INTERVAL"])),
        "SKIP_REDOWNLOAD": os.getenv('SKIP_REDOWNLOAD', 'false').lower() == 'true',
        "DRY_RUN": os.getenv('DRY_RUN', 'false').lower() == 'true'
    }

    initialize_logging(os.getenv('LOG_LEVEL', DEFAULTS["LOG_LEVEL"]))
    session.headers.update({
        'Content-Type': 'application/json',
        'X-Api-Key': env_vars["API_KEY"]
    })

    logging.info("Environment variables loaded successfully")
    return env_vars


def api_call(base_url, endpoint, method='GET', params=None, payload=None):
    url = f"{base_url}{endpoint}"
    try:
        response = session.request(method, url, params=params, json=payload)
        response.raise_for_status()
        return response.json() if response.text else None
    except requests.RequestException as e:
        logging.error(f"API call failed. Error: {e}")
        return None


def refresh_queue(base_url):
    response = api_call(base_url, "command", method='POST', payload={"name": "RefreshMonitoredDownloads"})
    if response and response.get('status') in ['started', 'queued']:
        logging.info("RefreshMonitoredDownloads command started successfully.")
        time.sleep(5)
        return True
    logging.error("RefreshMonitoredDownloads command failed to start.")
    return False


def get_stalled_ids(records):
    conditions = [is_stalled, has_sample_message, has_no_files_found_message]
    return [record['id'] for record in records if any(condition(record) for condition in conditions)]


def is_stalled(record):
    return 'errorMessage' in record and any(
        msg in record['errorMessage'] for msg in [
            'The download is stalled with no connections',
            'is downloading metadata'
        ]
    )


def has_sample_message(record):
    return any(
        'Sample' in message.get('title', '') or 'Sample' in ' '.join(message.get('messages', []))
        for message in record.get('statusMessages', [])
    )


def has_no_files_found_message(record):
    return any(
        'No files found are eligible for import in' in message.get('title', '') or
        'No files found are eligible for import in' in ' '.join(message.get('messages', []))
        for message in record.get('statusMessages', [])
    )


def process_queue(base_url, skip_redownload, dry_run):
    queue_info = api_call(base_url, 'queue', params={'page': 1, 'pageSize': 250, 'includeUnknownSeriesItems': True})
    if queue_info:
        records = queue_info.get('records', [])
        stalled_ids = get_stalled_ids(records)
        if stalled_ids:
            if dry_run:
                logging.info(f"[DRY RUN] Would have blacklisted {len(stalled_ids)} stalled records: {stalled_ids}")
            else:
                success = api_call(
                    base_url, 'queue/bulk', method='DELETE',
                    params={'removeFromClient': True, 'blocklist': True, 'skipRedownload': skip_redownload, 'changeCategory': False},
                    payload={"ids": stalled_ids}
                )
                if success:
                    logging.info(f"Successfully blacklisted {len(stalled_ids)} stalled records.")
                else:
                    logging.error("Failed to blacklist stalled records.")


def main():
    env_vars = fetch_env_vars()
    base_url = f'{env_vars["PROTOCOL"]}://{env_vars["HOST"]}:{env_vars["PORT"]}/api/v3/'

    while True:
        logging.info("Refreshing monitored downloads...")
        if refresh_queue(base_url):
            process_queue(base_url, env_vars['SKIP_REDOWNLOAD'], env_vars['DRY_RUN'])
        else:
            logging.error("Failed to refresh monitored downloads.")

        if env_vars['INTERVAL'] == 0:
            break
        logging.info(f"Sleeping for {env_vars['INTERVAL']} seconds.")
        time.sleep(env_vars['INTERVAL'])


if __name__ == "__main__":
    main()
