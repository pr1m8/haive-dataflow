# haive-dataflow

haive dataflow for the Haive framework.

## Installation

```bash
pip install haive-dataflow
```

## Database Setup

### Using Docker Compose (Recommended)

1. Start the PostgreSQL database:

```bash
cd packages/haive-dataflow
docker-compose up -d
```

2. Initialize the database schema:

```bash
poetry run init-db
```

### Manual Setup

If you prefer to use an existing PostgreSQL database:

1. Set the following environment variables:

```bash
export POSTGRES_HOST=your-db-host
export POSTGRES_PORT=5432
export POSTGRES_DB=your-db-name
export POSTGRES_USER=your-db-user
export POSTGRES_PASSWORD=your-db-password
export POSTGRES_SSL_MODE=prefer
```

2. Initialize the database schema:

```bash
poetry run init-db
```

## Usage

```python
from haive_dataflow import *

# Thread persistence with Supabase auth
from haive_dataflow.supabase import get_persistence_integration

# Get the persistence integration
persistence = get_persistence_integration()

# Prepare for an agent run
config, thread_id = persistence.prepare_for_agent_run(user_info=user_info)
```

## License

MIT
