import os
import time
import requests
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Fetch environment variables
HOST = os.getenv('HOST')  # Sonarr host IP and port
API_KEY = os.getenv('API_KEY')  # Sonarr API key
INTERVAL = int(os.getenv('INTERVAL', 3600))  # Default is 3600 seconds (1 hour)
REDOWNLOAD = os.getenv('REDOWNLOAD', False)  # Default is False

# Log environment variables for debugging
logging.info(f"Starting script with the following environment variables:")
logging.info(f"HOST: {HOST}")
logging.info(f"API_KEY: {'x' * (len(API_KEY) - 6) + API_KEY[-6:]}")
logging.info(f"INTERVAL: {INTERVAL}")
logging.info(f"REDOWNLOAD: {REDOWNLOAD}")
logging.info('-' * 50)

# Check for missing environment variables
if not HOST or not API_KEY:
    logging.error("Missing required environment variables. Please set HOST and API_KEY.")
    exit(1)

def api_call(base_url, endpoint, headers, method='GET', params=None, retries=3):
    url = f"{base_url}{endpoint}"
    for _ in range(retries):
        try:
            r = getattr(requests, method.lower())(url, headers=headers, params=params)
            r.raise_for_status()
            if r.text:
                return r.json()
            return None
        except requests.HTTPError as e:
            if r.text:
                error_message = r.json().get('message', 'Unknown error')
            else:
                error_message = 'No additional information'
            logging.error(f"API call failed with status code {r.status_code}. Error: {error_message}")

    logging.error(f"API call failed after {retries} retries")
    return None

while True:
    BASE_URL = f'http://{HOST}/api/v3/'
    HEADERS = {'Content-Type': 'application/json', 'X-Api-Key': API_KEY}

    # Initial parameters
    queue_params = {
        'page': 1,
        'pageSize': 250,
        'includeUnknownSeriesItems': True
    }

    queue_info = api_call(BASE_URL, 'queue', HEADERS, params=queue_params)
    if queue_info:
        total_items = queue_info['totalRecords']
        logging.info(f'Total Items in Queue: {total_items}')

        # Update pageSize to fetch all records
        queue_params['pageSize'] = total_items
        records = api_call(BASE_URL, 'queue', HEADERS, params=queue_params)
        if records:
            records = records['records']
            stalled_ids = [
                record['id'] for record in records
                if 'errorMessage' in record and
                (record['errorMessage'] == 'The download is stalled with no connections' or
                 record['errorMessage'] == 'qBittorrent is downloading metadata')
            ]

            logging.info(f"IDs of Stalled Records: {stalled_ids}")

            # Blacklist the stalled records
            for stalled_id in stalled_ids:
                params = {'removeFromClient': True, 'blocklist': True, 'skipRedownload': REDOWNLOAD}
                response = api_call(BASE_URL, f"queue/{stalled_id}", HEADERS, method='DELETE', params=params)
                if response:
                    logging.info(f"Successfully blacklisted record with ID {stalled_id}")

    logging.info(f"Sleeping for {INTERVAL} seconds.")
    time.sleep(INTERVAL)
