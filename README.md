# GPU Monitor

A Flask-based application for monitoring GPU, CPU, and memory status on remote servers. This project supports deployment using Docker and can be configured via an external `config.yaml` file.

## Features

- Monitors GPU, CPU, and memory usage on remote servers via SSH.
- Displays real-time status updates in a web interface.
- Configurable via an external YAML file.
- Deployable as a Docker container.
- Includes a production-ready setup using Gunicorn.

## Requirements

- Python 3.9 or higher
- Docker (optional for containerized deployment)
- SSH access to target servers
- A valid `config.yaml` file

## Project Structure

GPU-Monitor/ 
├── app.py # Main application file 
├── config/ 
│ └── config.yaml # Configuration file (external) 
├── requirements.txt # Python dependencies 
├── Dockerfile # Docker image definition 
├── docker-compose.yml # Docker Compose configuration 
└── templates/ 
└── index.html # Flask HTML template