#!/bin/bash
set -e

echo "Waiting for database to be ready..."
# Wait for PostgreSQL to be ready
until PGPASSWORD="${POSTGRES_PASSWORD:-stacknori}" psql -h "${POSTGRES_HOST:-db}" -U "${POSTGRES_USER:-stacknori}" -d "${POSTGRES_DB:-stacknori}" -c '\q' 2>/dev/null; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing migrations"

# Set ALEMBIC_DATABASE_URL if not set
if [ -z "$ALEMBIC_DATABASE_URL" ]; then
  export ALEMBIC_DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER:-stacknori}:${POSTGRES_PASSWORD:-stacknori}@${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-stacknori}"
fi

# Run migrations
alembic upgrade head

echo "Migrations completed successfully"

# Execute the main command
exec "$@"

