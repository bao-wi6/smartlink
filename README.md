# Flask Downlink API

This is a Flask application for managing LoRaWAN downlinks.

## Requirements

- Python 3.9+
- Flask
- requests

## Running Locally

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Run the Flask app:

    ```bash
    python app.py
    ```

The app will be available at `http://0.0.0.0:8686/`.

## Running with Docker

1. Build the Docker image:

    ```bash
    docker build -t flask-downlink-api .
    ```

2. Run the Docker container:

    ```bash
    docker run -p 8686:8686 flask-downlink-api
    ```

The app will be available at `http://0.0.0.0:8686/`.

## API Endpoint

### POST /apiv3/deviceManagement/lorawan-downlinks/smart/<device_id>/

- **Description**: Send a downlink command to a specified device.
- **Headers**:
  - `Authorization`: Bearer token required.
- **Request Body**:
  - JSON with `fport`, `type`, `ref`, and `value` fields.
