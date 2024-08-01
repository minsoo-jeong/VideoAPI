#!/bin/bash

set -x
# Get the list of process IDs for celery processes
pids=$(ps aux | grep '[c]elery -A app.celery_app' | awk '{print $2}')

echo $pids
# Iterate through each process ID and kill it
for pid in $pids
do
  echo "Stopping process ID $pid"
  kill $pid
done

echo "All Celery processes stopped."