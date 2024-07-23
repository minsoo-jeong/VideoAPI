#!/usr/bin/env bash

script_dir="$(dirname "$(readlink -f "$0")")"
parent_dir="$(dirname "$script_dir")"

# 부모 디렉토리로 이동
cd "$parent_dir" || { echo "Failed to change directory to $parent_dir"; exit 1; }


celery -A app.celery_app flower &
celery -A app.celery_app worker -l info -c 4 &

## 로그 디렉토리 설정
#log_dir="$parent_dir/logs"
#mkdir -p "$log_dir"
# Celery Flower 및 워커 로그 파일 설정
#flower_log_file="$log_dir/flower.log"
#worker_log_file="$log_dir/worker.log"
#
## Celery Flower nohup 백그라운드 실행 및 로그 파일에 기록
#nohup celery -A app.celery_app flower > "$flower_log_file" 2>&1 &
#
## Celery 워커 nohup 백그라운드 실행 및 로그 파일에 기록
#nohup celery -A app.celery_app worker -l info -c 4 > "$worker_log_file" 2>&1 &