# GPU Monitor

A Flask-based application for monitoring GPU, CPU, and memory status on remote servers. This project supports deployment
using Docker and can be configured via an external `config.yaml` file.

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

## Configuration

Create a `config.yaml` file in the `config/` directory with the following structure:

```yaml
servers:
  - name: "Server 1"
    hostname: "192.168.1.1"
    port: 22
    username: "user"
    password: "password"
  - name: "Server 2"
    hostname: "192.168.1.2"
    port: 22
    username: "user"
    password: "password"
refresh_interval: 5  # Interval (in seconds) for updating server status
```

## Installation (Local)

### Clone the repository:

```bash
git clone https://github.com/MiracleHYH/GPUMonitor.git
cd gpu-monitor
```

### Install dependencies:

```bash
pip install -r requirements.txt

```

### Run the application:

```bash
python flask run
```

### Access the web interface at http://localhost:5000.

## QuickStart (Docker)

### Create a `config` directory and add a `config.yaml` file with the desired configuration.

```bash
mkdir config && touch config/config.yaml
```

### Run the Docker container:

```bash
docker run -d -p 5000:5000 -v ./config:/app/config miraclehyh/gpu-monitor:latest
```

## QuickStart (Docker Compose)

### Create a `config` directory and add a `config.yaml` file with the desired configuration.

```bash
mkdir config && touch config/config.yaml
```

### Create a `docker-compose.yml` file from the following template:

```yaml
version: "3.9"

services:
  gpu-monitor:
    image: miracle996/gpu-monitor:latest
    container_name: gpu-monitor
    ports:
      - "5000:5000"
    volumes:
      - ./config/:/app/config/
    environment:
      - TZ=Asia/Shanghai
    restart: always
```

### Run the Docker Compose stack:

```bash
docker-compose up -d
```