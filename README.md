
# Cast-O-Matic

Smart classroom projector and presentation automation system.

## Features

- Epson projector control
- Power ON/OFF commands
- HDMI and wireless input selection
- PDF presentation upload
- Live screen sharing using WebRTC
- Real-time signaling using Flask-SocketIO
- Virtual projector receiver
- Docker containerization
- Kubernetes deployment
- Jenkins CI/CD pipeline

## Technology Stack

- Python 3.11
- Flask
- Flask-SocketIO
- JavaScript
- WebRTC
- HTML and CSS
- Docker
- Kubernetes
- Jenkins

## Installation

Install dependencies:

    python -m pip install -r requirements.txt

## Run Application

    python app.py

## Access Application

Main dashboard:

    http://127.0.0.1:5080/

Sender dashboard:

    http://127.0.0.1:5080/sender

Receiver dashboard:

    http://127.0.0.1:5080/receiver

## Docker

Build:

    docker build -t cast-o-matic:latest .

Run:

    docker run -p 5080:5080 cast-o-matic:latest

## Kubernetes

Apply deployment:

    kubectl apply -f deployment.yaml

Apply service:

    kubectl apply -f services.yaml

Check pods:

    kubectl get pods

Check services:

    kubectl get services

## Jenkins

The Jenkins pipeline performs:

1. Source code checkout
2. Dependency installation
3. Unit testing
4. Docker image build

## Project Structure

    cast-o-matic/
    |
    |-- app.py
    |-- requirements.txt
    |-- Dockerfile
    |-- Jenkinsfile
    |-- deployment.yaml
    |-- services.yaml
    |-- README.md
    |
    |-- templates/
    |   |-- index.html
    |   |-- sender.html
    |   |-- receiver.html
    |
    |-- uploads/
    |
    |-- tests/
        |-- __init__.py
        |-- test_guard.py
