# Sonarr Queue Manager (SQM)

This is a simple script for managing the queue in Sonarr. You can use it to blacklist stalled downloads, and optionally redownload them.  

Why the short name SQM you ask? Well, maybe we can add Radarr support in the future.  
So the name becomes Servarr Queue Manager.

## Getting Started

Follow these instructions to get the project up and running on your local machine for testing and development purposes.

### Prerequisites

- Docker
- Docker Compose (optional)

## Usage
#### Docker Compose

1. Rename the .env.example file to .env and fill in the required variables.

2. Run the following command to start the container:  
   ```docker-compose up -d```

#### Docker

1. Run the following command to start the container:  
   ```docker run -e HOST=192.168.x.x -e API_KEY=your-api-key -e INTERVAL=900 -e REDOWNLOAD=False -d --name sqm dkge/sqm:latest```

## Contributing

Contributions are welcome! If you'd like to improve this project, please open an issue to discuss a proposed change.

## Tested On
* Sonarr v4

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 