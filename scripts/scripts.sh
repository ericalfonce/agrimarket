#!/bin/bash

TIMESTAMP=$(date +"%Y%m%d_%H%M")
FILE="/backups/agrimarket_$TIMESTAMP.sql.gz"

pg_dump agrimarket | gzip > $FILE
rclone copy $FILE gdrive:agrimarket-backups

psql agrimarket -c \
"INSERT INTO backups (backup_time, status) VALUES (now(), 'SUCCESS');"
