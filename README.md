# Sonarr Queue Manager (SQM)

This is a simple web-based tool for managing the queue in Sonarr. You can use it to blacklist stalled downloads, and optionally redownload them.  

Why the short name SQM you ask? Well, maybe we can add Radarr support in the future.  
So the name becomes Servarr Queue Manager.

## Getting Started

Follow these instructions to get the project up and running on your local machine for testing and development purposes.

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/MrDKGE/SQM-Python.git
    ```

## Usage

1. Go to the projects directory in your web server's root directory.

2. Fill in the Sonarr server details:
    * IP Address
    * Port
    * API Key
    * Protocol (HTTP or HTTPS)
3. Optionally, check the "Save Details Locally" checkbox to save your settings for future visits.
4. Click the "Fetch Queue" button to retrieve the stalled downloads from your Sonarr server.
5. The list of stalled downloads will be displayed. You can select individual downloads for blacklisting.
6. Click the "Blacklist Selected" button to blacklist the selected downloads. You can also choose to redownload them by checking the "Redownload blacklisted items" checkbox.

## Contributing

Contributions are welcome! If you'd like to improve this project, follow these steps:

1. Fork the repository on GitHub.
2. Clone your forked repository to your local machine.
3. Create a new branch for your feature or bug fix:  
   ```git checkout -b feature/your-feature-name```
4. Make your changes and commit them:  
   ```git commit -m "Add your commit message here"```
5. Push your changes to your fork on GitHub:  
   ```git push origin feature/your-feature-name```
6. Create a pull request on GitHub from your forked repository to the main repository.
7. Describe your changes in the pull request, and the maintainers will review your code.

## Tested On
* Sonarr v4

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 