# Servarr Queue Manager (SQM)

[![GitHub](https://img.shields.io/badge/GitHub-SQM_Python-blue)](https://github.com/MrDKGE/SQM-Python)  
[![GitHub last commit](https://img.shields.io/github/last-commit/MrDKGE/SQM-Python)](https://github.com/MrDKGE/SQM-Python)  
[![Docker Pulls](https://img.shields.io/docker/pulls/dkge/sqm.svg)](https://hub.docker.com/r/dkge/sqm)  
[![Docker Stars](https://img.shields.io/docker/stars/dkge/sqm.svg)](https://hub.docker.com/r/dkge/sqm)  
[![Docker Image Size (tag)](https://img.shields.io/docker/image-size/dkge/sqm/latest)](https://hub.docker.com/r/dkge/sqm)  
[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/dkge/sqm)](https://hub.docker.com/r/dkge/sqm)

SQM is a lightweight Python tool designed to manage the download queues in Sonarr or Radarr. It monitors your queue at regular intervals, identifies stalled downloads based on certain conditions, and automatically blacklists them (with an option to skip redownload). This tool is built with robust logging and error handling, making it ideal for both testing and production use.

---

## Configuration

SQM uses a `config.json` file for its configuration. Place this file in the container’s working directory. **Please ensure your configuration file follows the order below:**

```json
{
  "interval": 3600,
  "dry_run": true,
  "log_level": "INFO",
  "stalled_policy": "immediate",
  "servers": [
    {
      "name": "Sonarr",
      "host": "192.168.1.x",
      "port": "18989",
      "protocol": "http",
      "api_key": "change_me",
      "skip_redownload": false
    },
    {
      "name": "Radarr",
      "host": "192.168.1.x",
      "port": "17878",
      "protocol": "http",
      "api_key": "change_me",
      "skip_redownload": false
    }
  ]
}
```

### Configuration Details

- **Global Settings:**
  - `interval`: Number of seconds between queue checks (set to `0` or a negative value to run a single iteration).
  - `dry_run`: When `true`, SQM simulates actions without making changes.
  - `log_level`: Determines the verbosity of logging (e.g., `INFO`, `DEBUG`).
  - `servers`: An array containing the configuration for each server.\
  - `stalled_policy`: New option to control stalled download removal behavior. Set to:
    - `immediate`: Removes stalled downloads as soon as they are detected.
    - `delayed`: Waits until a download is detected as stalled in two consecutive scans before removing it.

- **Per-Server Settings:**
  - `name`: A friendly name for the server (e.g., "Sonarr" or "Radarr").
  - `host`: The IP address of the server.
  - `port`: The server’s port (provided as a string).
  - `protocol`: The protocol to use (`http` or `https`).
  - `api_key`: Your API key for accessing the server’s API.
  - `skip_redownload`: When `true`, prevents redownload after blacklisting stalled downloads.

---

## What It Does

SQM continuously monitors your Sonarr/Radarr download queues. It checks for downloads that:
- Are stalled,
- Are "downloading metadata," or
- Contain messages indicating a sample file.

When such downloads are detected, SQM will blacklist them and, depending on your configuration, may skip their redownload.

---

## Docker Usage

Docker is the primary method for running SQM. Follow these instructions to get started:

### Running with Docker

1. **Prepare Your Config File:**  
   Create your `config.json` file (as shown above) on your host system.

2. **Run the Container:**  
   Mount your configuration file into the container:
   ```bash
   docker run -v /path/to/your/config.json:/app/config.json -d --name sqm dkge/sqm:latest
   ```

### Docker Compose Example

For those using Docker Compose, here is an example `docker-compose.yml` that runs SQM for multiple servers (e.g., Sonarr and Radarr):

```yaml
version: '3'

services:
  sqm:
    container_name: SQM
    image: dkge/sqm:latest
    volumes:
      - /path/to/your/config.json:/app/config.json
      - /etc/localtime:/etc/localtime:ro
    restart: always
```

*Note:* Replace `/path/to/your/…` with the actual paths to your configuration file(s) on your host system.

---

## Running Locally

If you prefer to run SQM without Docker:
1. Ensure the `config.json` file is in the same directory as the script.
2. Execute the script with Python:
   ```bash
   python sqm.py
   ```

---

## Contributing

Contributions are welcome! If you have suggestions or improvements, please open an issue or submit a pull request on our [GitHub repository](https://github.com/MrDKGE/SQM-Python).

---

## Tested On

- Sonarr v4.0.1.1047
- Radarr v5.3.4.8567
- qBittorrent v4.5.5

---

Explore SQM, configure it for your needs, and enjoy automated queue management for your media servers!