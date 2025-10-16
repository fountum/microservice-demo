#!/usr/bin/env bash
echo "Creating mongo users..."
mongo admin --host localhost -u root -p root --eval "db.createUser({user: 'processing_api', pwd: 'dubsowl', roles: [{role: 'readWrite', db: 'sales_stats'}]}); db.createUser({user: 'admin', pwd: 'PASS', roles: [{role: 'userAdminAnyDatabase', db: 'admin'}]});"
echo "Mongo users created."
