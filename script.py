import os
import sys
import time
import json
import requests
import datetime
from collections import defaultdict


class QueueManager:
    """Handles queue operations and download management."""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.session = requests.Session()
        
        # Patterns to detect different types of issues
        self.stalled_patterns = [
            "The download is stalled with no connections",
            "is downloading metadata"
        ]
        
        self.problem_patterns = [
            "Sample",
            "No files found are eligible for import in",
            "Found potentially dangerous file with extension:"
        ]
    
    def load_stalled_downloads(self):
        """Load previously stalled downloads from file."""
        filename = 'stalled_downloads.json'
        if not os.path.exists(filename):
            return {}
        
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except:
            print("Warning: Could not load stalled downloads file")
            return {}
    
    def save_stalled_downloads(self, data):
        """Save stalled downloads to file."""
        try:
            with open('stalled_downloads.json', 'w') as f:
                json.dump(data, f, indent=2)
        except:
            print("Warning: Could not save stalled downloads file")
    
    def api_call(self, url, api_key, method='GET', params=None, data=None):
        """Make API call to server."""
        headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': api_key
        }
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, headers=headers, json=data, timeout=30)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, params=params, json=data, timeout=30)
            
            if response.status_code == 401:
                print("Error: Authentication failed - check your API key")
                return None
            
            response.raise_for_status()
            return response.json() if response.text else {}
            
        except requests.exceptions.RequestException as e:
            print(f"API call failed: {e}")
            return None
    
    def check_download_issues(self, record):
        """Check if download has issues and return issue type."""
        error_message = record.get('errorMessage', '')
        
        # Check for stalled downloads
        for pattern in self.stalled_patterns:
            if pattern in error_message:
                return 'stalled'
        
        # Check for problematic downloads (samples, dangerous files, etc.)
        for pattern in self.problem_patterns:
            if pattern in error_message:
                return 'problem'
            
            # Also check status messages
            for msg in record.get('statusMessages', []):
                title = msg.get('title', '')
                if pattern in title:
                    return 'problem'
                
                for sub_msg in msg.get('messages', []):
                    if pattern in str(sub_msg):
                        return 'problem'
        
        return None
    
    def categorize_downloads(self, records):
        """Sort downloads into categories: problems (remove now) and stalled."""
        problem_ids = []
        stalled_ids = []
        
        # Group by download ID to handle season packs
        download_groups = defaultdict(list)
        for record in records:
            download_id = record.get('downloadId', record['id'])
            download_groups[download_id].append(record)
        
        # Check each group
        for download_id, group in download_groups.items():
            if len(group) > 1:
                print(f"Found season pack with {len(group)} episodes")
            
            # Check the first record (represents the whole group)
            record = group[0]
            issue_type = self.check_download_issues(record)
            
            if issue_type == 'problem':
                problem_ids.append(record['id'])
                print(f"Problem download: {record.get('title', 'Unknown')}")
            elif issue_type == 'stalled':
                stalled_ids.append(record['id'])
        
        return problem_ids, stalled_ids
    
    def remove_downloads(self, server, download_ids, description):
        """Remove downloads from queue."""
        if not download_ids:
            return True
        
        if self.dry_run:
            print(f"[DRY RUN] Would remove {len(download_ids)} {description}")
            return True
        
        url = f"{server['protocol']}://{server['host']}:{server['port']}/api/v3/queue/bulk"
        params = {
            'removeFromClient': True,
            'blocklist': True,
            'skipRedownload': server['skip_redownload'],
            'changeCategory': False
        }
        
        result = self.api_call(url, server['api_key'], method='DELETE', 
                              params=params, data={"ids": download_ids})
        
        if result is not None:
            print(f"Successfully removed {len(download_ids)} {description}")
            return True
        else:
            print(f"Failed to remove {description}")
            return False
    
    def process_server(self, server, stalled_policy):
        """Process queue for one server."""
        print(f"\nProcessing server: {server['name']}")
        
        base_url = f"{server['protocol']}://{server['host']}:{server['port']}/api/v3"
        
        # Refresh the queue first
        refresh_url = f"{base_url}/command"
        refresh_result = self.api_call(refresh_url, server['api_key'], method='POST',
                                     data={"name": "RefreshMonitoredDownloads"})
        
        if not refresh_result or refresh_result.get('status') not in ['started', 'queued']:
            print("Warning: Queue refresh may have failed")
        else:
            print("Queue refresh started")
            time.sleep(5)  # Wait for refresh to complete
        
        # Get queue data
        queue_url = f"{base_url}/queue"
        params = {'page': 1, 'pageSize': 250, 'includeUnknownSeriesItems': True}
        queue_data = self.api_call(queue_url, server['api_key'], params=params)
        
        if not queue_data:
            print("Failed to get queue data")
            return
        
        records = queue_data.get('records', [])
        if not records:
            print("Queue is empty")
            # Clear stalled downloads for this server if using delayed policy
            if stalled_policy == "delayed":
                data = self.load_stalled_downloads()
                data[server['name']] = []
                self.save_stalled_downloads(data)
            return
        
        print(f"Found {len(records)} items in queue")
        
        # Categorize downloads
        problem_ids, current_stalled_ids = self.categorize_downloads(records)
        
        # Remove problematic downloads immediately
        if problem_ids:
            self.remove_downloads(server, problem_ids, "problematic downloads")
        
        # Handle stalled downloads based on policy
        if stalled_policy == "delayed":
            # Load previous stalled downloads
            data = self.load_stalled_downloads()
            previous_stalled = set(data.get(server['name'], []))
            current_stalled = set(current_stalled_ids)
            
            # Remove downloads that were stalled in previous run too
            confirmed_stalled = list(current_stalled.intersection(previous_stalled))
            still_stalled = current_stalled - set(confirmed_stalled)
            
            # Save currently stalled for next run
            data[server['name']] = list(still_stalled)
            self.save_stalled_downloads(data)
            
            if confirmed_stalled:
                self.remove_downloads(server, confirmed_stalled, "confirmed stalled downloads")
            elif current_stalled:
                print(f"Found {len(current_stalled)} stalled downloads - will remove if still stalled next scan")
        else:
            # Immediate removal
            if current_stalled_ids:
                self.remove_downloads(server, current_stalled_ids, "stalled downloads")
            
            # Clear stalled downloads file
            data = self.load_stalled_downloads()
            data[server['name']] = []
            self.save_stalled_downloads(data)


def load_config():
    """Load configuration from config.json file."""
    if not os.path.exists('config.json'):
        print("Error: config.json file not found")
        sys.exit(1)
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("Configuration loaded successfully")
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)


def main():
    """Main function."""
    # Load configuration
    config = load_config()
    
    # Create queue manager
    queue_manager = QueueManager(dry_run=config.get('dry_run', False))
    
    # Get settings
    servers = config['servers']
    interval = config.get('interval', 300)
    stalled_policy = config.get('stalled_policy', 'immediate')
    
    print(f"Loaded {len(servers)} server(s)")
    print(f"Stalled policy: {stalled_policy}")
    
    if config.get('dry_run'):
        print("DRY RUN MODE - No actual changes will be made")
    
    try:
        while True:
            # Process each server
            for server in servers:
                try:
                    queue_manager.process_server(server, stalled_policy)
                except Exception as e:
                    print(f"Error processing {server['name']}: {e}")
            
            # Check if we should run only once
            if interval <= 0:
                print("Single run mode - exiting")
                break
            
            # Wait for next scan
            next_scan = datetime.datetime.now() + datetime.timedelta(seconds=interval)
            print(f"\nNext scan at: {next_scan.strftime('%H:%M:%S')}")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()