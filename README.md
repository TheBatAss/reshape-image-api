# reshape-image-api

## Prerequisites

- Python 3.x
- pip
- Docker
- docker-compose

## Running locally

1. Install the project dependencies by running the following command:

```
 pip install -r requirements.txt
```

2. On linux you might have to install additional dependencies `ffmpeg`, `libsm6` and `libxext6`

3. Start the Flask server by running the following command:

```
python app.py
```

3. The API is now running on http://localhost:5000/

## Running with Docker Compose

- Start up the API (might take a minute the first time around)

```
docker-compose up
```

- Teardown the API

```
docker-compose down
```
