# Sonarr Queue Manager (SQM)

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