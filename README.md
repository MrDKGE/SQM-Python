# Sonarr Queue Manager (SQM)

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

| Variable        | Description                                    | Default   | Required |
|:----------------|:-----------------------------------------------|:----------|:---------|
| HOST            | The IP address of the Sonarr host              | 127.0.0.1 | No       |
| PORT            | The port of the Sonarr host                    | 8989      | No       |
| PROTOCOL        | The protocol of the Sonarr host                | http      | No       |
| API_KEY         | The API key of the Sonarr host                 |           | Yes      |
| INTERVAL        | The interval in seconds between each check     | 3600      | No       |
| SKIP_REDOWNLOAD | Whether or not to redownload stalled downloads | False     | No       |
| LOG_LEVEL       | The log level                                  | INFO      | No       |

## What does it do?

The script will check the queue in Sonarr every x seconds (default 3600 seconds).
If certain conditions are met, the script will blacklist the download and optionally redownload it.  
Conditions:

- Status is Stalled
- Downloading metadata
- Title or status message contains "sample"

## Getting Started

Follow these instructions to get the project up and running on your local machine for testing and development purposes.

### Prerequisites

- Docker
- Docker Compose (optional)

## Usage

#### Docker Compose

Rename the .env.example file to .env and fill in the required variables.  
Run the following command to start the container:

```
docker-compose up -d
```

#### Docker

Run the following command to start the container:

```
docker run -e HOST=192.168.x.x -e API_KEY=your-api-key -d --name sqm dkge/sqm:latest
```

## Contributing

Contributions are welcome! If you'd like to improve this project, please open an issue to discuss a proposed change.

## Tested On

* Sonarr v4
* qBittorrent v4.5.5

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 