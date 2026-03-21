#!/bin/bash

set -e

echo "Starting database initialization for Doomscroll..."

# Check if necessary environment variables are set
: "${POSTGRES_USER:?Environment variable POSTGRES_USER is required}"
: "${POSTGRES_PASSWORD:?Environment variable POSTGRES_PASSWORD is required}"
: "${POSTGRES_DB:?Environment variable POSTGRES_DB is required}"

# Connect to PostgreSQL and test connection
echo "Testing PostgreSQL connection..."
PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SELECT 'Connected to PostgreSQL successfully'" || {
    echo "Failed to connect to PostgreSQL. Check your credentials and database status."
    exit 1
}

echo "Creating database extensions..."
PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -U ${POSTGRES_USER} -d ${POSTGRES_DB} <<-EOSQL
    -- Create extensions if needed
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Grant privileges
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${POSTGRES_USER};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${POSTGRES_USER};

    SELECT 'Extensions created successfully' as status;
EOSQL

echo "Database initialization completed."
echo "Note: Tables are created via Alembic migrations."
echo "Run 'alembic upgrade head' from the backend directory."
