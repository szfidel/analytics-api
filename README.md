# Analytics API using FastAPI + TimescaleDB + PostgreSQL

Version 1

- Purpose: Time-series event data collection and aggregation using TimescaleDB
- Tech Stack: FastAPI, PostgreSQL + TimescaleDB, SQLModel, Uvicorn
- Key Features:
  - Event ingestion (POST /api/events/)
  - Event querying with time-bucketing and aggregation (GET /api/events/)
  - Single event retrieval (GET /api/events/{event_id})
  - Support for multiple signal types (relational, emotional, behavioral)
  - Metrics like emotional tone, drift score tracking
  - Health check endpoint
- Data Model: Events with timestamps, user IDs, agent IDs, signal types, and computed metrics
- Deployment: Docker + Docker Compose with TimescaleDB integration

## Docker

Build image

- `docker build -t analytics-api -f Dockerfile.web .`
  Run container
- `docker run analytics-api `

- `docker compose run app /bin/bash` or `docker compose run app python`

# Quick Start

## Prerequisites

- Docker & Docker Compose
- Python 3.13+ (for local development)

## Run with Docker Compose

### Start the API and database

`docker compose up --build`

### Or with hot-reload enabled

`docker compose up --watch`
The API will be available at http://localhost:8002

### Run interactive bash in container

`docker compose run app /bin/bash`

### Or run Python REPL

`docker compose run app python`

### Stop containers

`docker compose down`

### Remove volumes (database data)

`docker compose down -v`

### Test the API:

curl http://localhost:8002/healthz
curl http://localhost:8002/
Clean Up

# API Endpoints

Health Check
GET /healthz
Returns {"status": "ok"}

Root
GET /
Simple test endpoint

Event Management
List Events (Aggregated)
GET /api/events/
Query Parameters:

- duration (string, default: "1 day"): Time bucket duration (e.g., "1 hour", "7 days")
- signal_types (array, optional): Filter by signal types. Defaults to ["relational", "emotional", "behavioral"]

# Dependencies

See requirements.txt:

- fastapi: Web framework
- uvicorn: ASGI server
- sqlmodel: SQLAlchemy ORM with Pydantic validation
- timescaledb: TimescaleDB Python client
- psycopg: PostgreSQL adapter (v3)
- python-decouple: Environment configuration
