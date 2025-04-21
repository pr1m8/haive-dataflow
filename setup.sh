#!/bin/bash

set -e

echo "=== Installing dependencies ==="
poetry install

echo "=== Starting PostgreSQL (if not already running) ==="
docker-compose up -d

echo "=== Waiting for PostgreSQL to be ready ==="
sleep 5

echo "=== Initializing database ==="
poetry run init-db

echo "=== Setup complete! ==="
echo "You can now use the haive-dataflow package with PostgreSQL persistence." 