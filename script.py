import os
import time
import requests
import logging

# Constants
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = "8989"
DEFAULT_INTERVAL = 3600
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Initialize logging
logging.basicConfig(level=LOG_LEVEL, format='%(levelname)s - %(message)s')


# Fetch and log environment variables
def fetch_env_vars():
    required_vars = {
        "API_KEY": os.getenv('API_KEY')
    }
    optional_vars = {
        "HOST": os.getenv('HOST', DEFAULT_HOST),
        "PORT": os.getenv('PORT', DEFAULT_PORT),
        "PROTOCOL": os.getenv('PROTOCOL', 'http'),
        "INTERVAL": int(os.getenv('INTERVAL', DEFAULT_INTERVAL)),
        "SKIP_REDOWNLOAD": os.getenv('SKIP_REDOWNLOAD', 'False').lower() == 'true'
    }

    if not all(required_vars.values()):
        logging.error("Missing required environment variables. Exiting.")
        exit(1)

    logging.info(f"Starting script with the following environment variables:")

    masked_api_key = 'x' * (len(required_vars['API_KEY']) - 6) + required_vars['API_KEY'][-6:]
    logging.info(f"API_KEY: {masked_api_key}")

    for var, value in optional_vars.items():
        logging.info(f"{var}: {value}")

    return required_vars, optional_vars


def api_call(base_url, endpoint, headers, method='GET', params=None):
    url = f"{base_url}{endpoint}"
    try:
        r = getattr(requests, method.lower())(url, headers=headers, params=params)
        r.raise_for_status()
        if method == 'DELETE':
            return True if r.status_code == 200 else None
        else:
            return r.json() if r.text else None
    except requests.HTTPError:
        error_message = r.json().get('message', 'Unknown error') if r.text else 'No additional information'
        logging.error(f"API call failed with status code {r.status_code}. Error: {error_message}")
        if r.status_code == 404:
            return None


def main():
    required_vars, optional_vars = fetch_env_vars()
    base_url = f'{optional_vars["PROTOCOL"]}://{optional_vars["HOST"]}:{optional_vars["PORT"]}/api/v3/'
    headers = {'Content-Type': 'application/json', 'X-Api-Key': required_vars['API_KEY']}

    while True:
        queue_params = {'page': 1, 'pageSize': 250, 'includeUnknownSeriesItems': True}
        queue_info = api_call(base_url, 'queue', headers, params=queue_params)

        if not queue_info:
            continue

        total_items = queue_info['totalRecords']
        logging.info(f'Total Items in Queue: {total_items}')

        queue_params['pageSize'] = total_items
        records = api_call(base_url, 'queue', headers, params=queue_params)['records'] if queue_info else []

        stalled_ids = [
            record['id'] for record in records
            if 'errorMessage' in record and (
                    'The download is stalled with no connections' in record['errorMessage'] or
                    'is downloading metadata' in record['errorMessage']
            ) or any(
                'Sample' in message.get('title', '') or 'Sample' in ' '.join(message.get('messages', []))
                for message in record.get('statusMessages', [])
            )
        ]

        logging.info(f"IDs of Stalled Records: {stalled_ids}")

        for stalled_id in stalled_ids:
            params = {'removeFromClient': True, 'blocklist': True, 'skipRedownload': optional_vars['SKIP_REDOWNLOAD']}
            if api_call(base_url, f"queue/{stalled_id}", headers, method='DELETE', params=params):
                logging.info(f"Successfully blacklisted record with ID {stalled_id}")
            else:
                logging.error(f"Failed to blacklist record with ID {stalled_id}")

        logging.info(f"Sleeping for {optional_vars['INTERVAL']} seconds.")
        time.sleep(optional_vars['INTERVAL'])


if __name__ == "__main__":
    main()
