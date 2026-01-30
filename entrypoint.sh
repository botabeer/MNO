#!/bin/bash

if [ "$ENV_MODE" = "dev" ]; then
    echo "Running in development mode"
    python app.py
else
    echo "Running in production mode"
    gunicorn app:app -c gunicorn_config.py
fi
