# Docker Setup Guide

## Overview

The Docker setup includes automatic database migration on container startup, ensuring your database schema is always up-to-date.

## Quick Start

### Build and Run

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

## Database Migration

### Automatic Migration

The database migration runs automatically when the API container starts via the `docker-entrypoint.sh` script. This ensures:

- ✅ New columns are added automatically
- ✅ Existing data is preserved
- ✅ Migration is idempotent (safe to run multiple times)

### Manual Migration

If you need to run migration manually:

```bash
# Run migration in running container
docker-compose exec api python database/migrate_schema.py

# Or run in a new container
docker-compose run --rm api python database/migrate_schema.py
```

## Services

### API Service
- **Port**: 8000
- **Auto-migration**: Yes (on startup)
- **Restart**: unless-stopped
- **Memory**: 2GB limit

### Redis Service
- **Port**: 6380 (host) → 6379 (container)
- **Health check**: Enabled
- **Restart**: always

### Celery Worker
- **Concurrency**: 2
- **Memory**: 4GB limit
- **Tasks**: Background processing

### Celery Beat
- **Memory**: 512MB limit
- **Purpose**: Scheduled tasks

### Flower
- **Port**: 5555
- **Purpose**: Celery monitoring

## Volume Mounts

- `.:/app` - Application code (hot reload in development)
- `./data:/app/data` - Database and logs persistence

## Environment Variables

### API Service
- `REDIS_URL=redis://redis:6379/0`
- `ENABLE_VOICE=false` (set to `true` for voice features)

### Celery Services
- `CELERY_BROKER_URL=redis://redis:6379/0`
- `CELERY_RESULT_BACKEND=redis://redis:6379/0`

## Development

### Hot Reload

The API service uses volume mounts for hot reload:

```bash
# Make changes to code
# Changes are reflected immediately (no rebuild needed)
```

### Rebuild After Dependency Changes

```bash
# Rebuild containers
docker-compose build

# Restart services
docker-compose up -d
```

## Production Considerations

1. **Database Backup**: Ensure `./data` directory is backed up
2. **Environment Variables**: Use `.env` file for secrets
3. **Resource Limits**: Adjust in `docker-compose.yml` based on usage
4. **SSL/TLS**: Add reverse proxy (nginx) for HTTPS
5. **Monitoring**: Set up health checks and monitoring

## Troubleshooting

### Migration Errors

If migration fails:
```bash
# Check logs
docker-compose logs api | grep Migration

# Run migration manually
docker-compose exec api python database/migrate_schema.py
```

### Database Issues

```bash
# Access database
docker-compose exec api sqlite3 data/ai_friend.db

# Backup database
docker-compose exec api cp data/ai_friend.db data/backups/ai_friend_$(date +%Y%m%d).db
```

### Container Issues

```bash
# Restart specific service
docker-compose restart api

# Rebuild and restart
docker-compose up -d --build api

# View resource usage
docker stats ai_friend_api
```

## Migration Script Details

The migration script (`database/migrate_schema.py`):

- ✅ Adds new columns to existing tables
- ✅ Preserves all existing data
- ✅ Safe to run multiple times
- ✅ Logs all changes
- ✅ Handles errors gracefully

**Tables Migrated**:
- `messages` - 9 new columns for training data
- `conversations` - 8 new columns for analytics
- `memories` - 7 new columns for metadata
- `agent_logs` - 5 new columns for quality tracking

## Example Workflow

```bash
# 1. Start services
docker-compose up -d

# 2. Check migration ran
docker-compose logs api | grep "Migration complete"

# 3. Verify API is running
curl http://localhost:8000/api/health

# 4. View all logs
docker-compose logs -f
```
