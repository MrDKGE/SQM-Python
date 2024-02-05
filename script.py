import os
import time
import requests
import logging

# Constants for defaults
DEFAULTS = {
    "HOST": "127.0.0.1",
    "PORT": "8989",
    "PROTOCOL": "http",
    "INTERVAL": 3600,
    "LOG_LEVEL": "INFO",
    "SKIP_REDOWNLOAD": False
}


# Function to fetch and validate environment variables
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
    }

    # Initialize logging
    logging.basicConfig(level=os.getenv('LOG_LEVEL', DEFAULTS["LOG_LEVEL"]).upper(), format='%(levelname)s - %(message)s')

    # Initialize session headers
    session.headers.update({'Content-Type': 'application/json', 'X-Api-Key': env_vars["API_KEY"]})

    logging.info("Environment variables loaded successfully")
    return env_vars


# Initialize a Session
session = requests.Session()


# API call function
def api_call(base_url, endpoint, method='GET', params=None, payload=None):
    url = f"{base_url}{endpoint}"
    try:
        response = session.request(method, url, params=params, json=payload)
        response.raise_for_status()
        return response.json() if response.text else None
    except requests.RequestException as e:
        logging.error(f"API call failed. Error: {e}")
        return None


# Function to refresh queue
def refresh_queue(base_url):
    payload = {"name": "RefreshMonitoredDownloads"}
    response = api_call(base_url, "command", method='POST', payload=payload)
    if response and response.get('status') in ['started', 'queued']:
        logging.info("RefreshMonitoredDownloads command started successfully.")
        time.sleep(5)  # Allow command to start
        return True
    logging.error("RefreshMonitoredDownloads command failed to start.")
    return False


# Function to get stalled IDs
def get_stalled_ids(records):
    return [record['id'] for record in records if any(condition(record) for condition in [is_stalled, has_sample_message])]


# Check if record is stalled
def is_stalled(record):
    return 'errorMessage' in record and ('The download is stalled with no connections' in record['errorMessage'] or 'is downloading metadata' in record['errorMessage'])


# Check if record has a sample message
def has_sample_message(record):
    return any('Sample' in message.get('title', '') or 'Sample' in ' '.join(message.get('messages', [])) for message in record.get('statusMessages', []))


# Process queue
def process_queue(base_url, skip_redownload):
    queue_info = api_call(base_url, 'queue', params={'page': 1, 'pageSize': 250, 'includeUnknownSeriesItems': True})
    if queue_info:
        records = queue_info.get('records', [])
        stalled_ids = get_stalled_ids(records)
        if stalled_ids:
            params = {'removeFromClient': True, 'blocklist': True, 'skipRedownload': skip_redownload, 'changeCategory': False}
            if api_call(base_url, 'queue/bulk', method='DELETE', params=params, payload={"ids": stalled_ids}):
                logging.info(f"Successfully blacklisted {len(stalled_ids)} stalled records.")
            else:
                logging.error("Failed to blacklist stalled records.")


# Main function
def main():
    env_vars = fetch_env_vars()
    base_url = f'{env_vars["PROTOCOL"]}://{env_vars["HOST"]}:{env_vars["PORT"]}/api/v3/'

    while True:
        logging.info("Refreshing monitored downloads...")
        if refresh_queue(base_url):
            process_queue(base_url, env_vars['SKIP_REDOWNLOAD'])
        else:
            logging.error("Failed to refresh monitored downloads.")

        if env_vars['INTERVAL'] == 0:
            break
        logging.info(f"Sleeping for {env_vars['INTERVAL']} seconds.")
        time.sleep(env_vars['INTERVAL'])


if __name__ == "__main__":
    main()
