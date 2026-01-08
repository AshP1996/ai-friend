#!/bin/bash
# Docker entrypoint script
# Runs database migration before starting the application

set -e

echo "🚀 Starting AI Friend API..."

# Run database migration (idempotent - safe to run multiple times)
echo "📊 Running database migration..."
if python database/migrate_schema.py; then
    echo "✅ Migration complete."
else
    echo "⚠️  Migration had warnings (this is normal if columns already exist)"
fi

# Start the application
echo "🚀 Starting API server..."
exec "$@"
