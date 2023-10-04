# Sonarr Queue Manager (SQM)

[![GitHub](https://img.shields.io/badge/GitHub-SQM_Python-blue)](https://github.com/MrDKGE/SQM-Python)
[![GitHub last commit](https://img.shields.io/github/last-commit/MrDKGE/SQM-Python)](https://github.com/MrDKGE/SQM-Python)
[![GitHub contributors](https://img.shields.io/github/contributors/MrDKGE/SQM-Python)](https://github.com/MrDKGE/SQM-Python/graphs/contributors)
[![Docker Pulls](https://img.shields.io/docker/pulls/dkge/sqm.svg)](https://hub.docker.com/r/dkge/sqm)
[![Docker Stars](https://img.shields.io/docker/stars/dkge/sqm.svg)](https://hub.docker.com/r/dkge/sqm)
[![Docker Image Size (tag)](https://img.shields.io/docker/image-size/dkge/sqm/latest)](https://hub.docker.com/r/dkge/sqm)
[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/dkge/sqm)](https://hub.docker.com/r/dkge/sqm)

This is a simple script for managing the queue in Sonarr. You can use it to blacklist stalled downloads, and optionally redownload them.

Why the short name SQM you ask? Well, maybe we can add Radarr support in the future.  
So the name becomes Servarr Queue Manager.

## Environment Variables

| Variable   | Description                                    | Default   | Required |
|:-----------|:-----------------------------------------------|:----------|:---------|
| HOST       | The IP address of the Sonarr host              | 127.0.0.1 | No       |
| PORT       | The port of the Sonarr host                    | 8989      | No       |
| PROTOCOL   | The protocol of the Sonarr host                | http      | No       |
| API_KEY    | The API key of the Sonarr host                 |           | Yes      |
| INTERVAL   | The interval in seconds between each check     | 3600      | No       |
| REDOWNLOAD | Whether or not to redownload stalled downloads | False     | No       |
| LOG_LEVEL  | The log level                                  | INFO      | No       |

## What does it do?

The script will check the queue in Sonarr every x seconds (default 3600 seconds).
If certain conditions are met, the script will blacklist the download and optionally redownload it.  
Conditions:

- Status is Stalled
- Downloading metadata
- Title or status message contains "sample"

## Usage

#### Docker Compose

```
version: '3'

services:
  sqm:
    container_name: SQM
    image: dkge/sqm:latest
    environment:
      - HOST=${HOST}
      - PORT=${PORT}
      - API_KEY=${API_KEY}
    restart: always
```

#### Docker

Run the following command to start the container:

```
docker run -e HOST=192.168.x.x -e API_KEY=your-api-key -d --name sqm dkge/sqm:latest
```

## Tested On

* Sonarr v4
* qBittorrent v4.5.5