# Servarr Queue Manager (SQM)

[![GitHub](https://img.shields.io/badge/GitHub-SQM_Python-blue)](https://github.com/MrDKGE/SQM-Python)
[![GitHub last commit](https://img.shields.io/github/last-commit/MrDKGE/SQM-Python)](https://github.com/MrDKGE/SQM-Python)
[![Docker Pulls](https://img.shields.io/docker/pulls/dkge/sqm.svg)](https://hub.docker.com/r/dkge/sqm)
[![Docker Stars](https://img.shields.io/docker/stars/dkge/sqm.svg)](https://hub.docker.com/r/dkge/sqm)
[![Docker Image Size (tag)](https://img.shields.io/docker/image-size/dkge/sqm/latest)](https://hub.docker.com/r/dkge/sqm)
[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/dkge/sqm)](https://hub.docker.com/r/dkge/sqm)

This is a simple script for managing the queue in Sonarr or Radarr. You can use it to blacklist stalled downloads, and optionally redownload them.

## Environment Variables

| Variable        | Description                                    | Default   | Required |
|:----------------|:-----------------------------------------------|:----------|:---------|
| HOST            | The IP address of the Sonarr/Radarr host       | 127.0.0.1 | No       |
| PORT            | The port of the Sonarr/Radarr host             | 8989      | No       |
| PROTOCOL        | The protocol of the Sonarr/Radarr host         | http      | No       |
| API_KEY         | The API key of the Sonarr/Radarr host          |           | Yes      |
| INTERVAL        | The interval in seconds between each check     | 3600      | No       |
| SKIP_REDOWNLOAD | Whether or not to redownload stalled downloads | False     | No       |
| LOG_LEVEL       | The log level                                  | INFO      | No       |

## What does it do?

The script will check the queue in Sonarr/Radarr every x seconds (default 3600 seconds).
If certain conditions are met, the script will blacklist the download and optionally redownload it.  
Conditions:

- Status is Stalled
- Downloading metadata
- Title or status message contains "sample"

## Usage
Note: You will have to replace the environment variables with your own values.

#### Docker

Run the following command to start the container:

```
docker run -e HOST=192.168.X.X -e API_KEY=your-api-key -d --name sqm dkge/sqm:latest
```

#### Docker Compose

In the example below, SQM will check both Sonarr and Radarr every 3 hours.
```yaml
version: '3'

services:
  sqm-1:
    container_name: SQM-Sonarr
    image: dkge/sqm:latest
    environment:
      - HOST=192.168.XX.XX
      - PORT=8989
      - API_KEY=XXXX
      - INTERVAL=10800
    restart: always

  sqm-2:
    container_name: SQM-Radarr
    image: dkge/sqm:latest
    environment:
      - HOST=192.168.XX.XX
      - PORT=7878
      - API_KEY=XXXX
      - INTERVAL=10800
    restart: always
```


## Contributing

Contributions are welcome! If you'd like to improve this project, please open an issue to discuss a proposed change.

## Tested On

* Sonarr v4.0.1.1047
* Radarr v5.3.4.8567
* qBittorrent v4.5.5