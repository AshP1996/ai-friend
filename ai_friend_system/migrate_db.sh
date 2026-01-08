#!/bin/bash
# Database migration helper script
# Makes it easy to run the migration with proper environment

cd "$(dirname "$0")"
source ../venv/bin/activate
python database/migrate_schema.py
