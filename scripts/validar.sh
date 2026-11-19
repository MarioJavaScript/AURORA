#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

failures=0
check() {
  local label="$1"
  shift
  if "$@"; then
    printf 'OK: %s\n' "$label"
  else
    printf 'FALLA: %s\n' "$label" >&2
    failures=$((failures + 1))
  fi
}

if [[ ! -f .env ]]; then
  printf 'FALLA: falta .env\n' >&2
  exit 1
fi

DB_USER=''
DB_PASSWORD=''
DB_NAME=''
while IFS='=' read -r key value || [[ -n "$key" ]]; do
  value="${value%$'\r'}"
  case "$value" in
    \"*\") value="${value:1:${#value}-2}" ;;
    \'*\') value="${value:1:${#value}-2}" ;;
  esac
  case "$key" in
    DB_USER) DB_USER="$value" ;;
    DB_PASSWORD) DB_PASSWORD="$value" ;;
    DB_NAME) DB_NAME="$value" ;;
  esac
done < .env

if [[ -z "$DB_USER" || -z "$DB_PASSWORD" || -z "$DB_NAME" ]]; then
  printf 'FALLA: DB_USER, DB_PASSWORD o DB_NAME faltan en .env\n' >&2
  exit 1
fi

health_ready() {
  [[ "$(curl -sS -o /dev/null -w '%{http_code}' --max-time 3 http://localhost/salud 2>/dev/null || true)" == 200 ]]
}

start=$SECONDS
until health_ready; do
  if (( SECONDS - start >= 120 )); then
    break
  fi
  sleep 2
done
check 'salud HTTP 200 (máximo 120 segundos)' health_ready

home_ready() {
  [[ "$(curl -sS -o /dev/null -w '%{http_code}' --max-time 3 http://localhost 2>/dev/null || true)" == 200 ]]
}
check 'inicio HTTP 200' home_ready

count_is() {
  local table="$1" expected="$2" actual
  actual="$(docker compose exec -T -e "MYSQL_PWD=$DB_PASSWORD" db mysql -u "$DB_USER" --batch --skip-column-names "$DB_NAME" -e "SELECT COUNT(*) FROM $table" 2>/dev/null)" || return 1
  [[ "$actual" == "$expected" ]]
}
check '8 tipos' count_is tipos 8
check '6 estados' count_is estados 6
check '12 equipos' count_is equipos 12

no_host_port() {
  local service="$1" container ports
  container="$(docker compose ps -q "$service")"
  [[ -n "$container" ]] || return 1
  ports="$(docker inspect --format '{{json .NetworkSettings.Ports}}' "$container")" || return 1
  [[ "$ports" != *'HostPort'* ]]
}
nginx_port_80() {
  local binding
  binding="$(docker compose port nginx 80)" || return 1
  [[ "$binding" =~ :80$ ]]
}
check 'app sin puerto publicado' no_host_port app
check 'db sin puerto publicado' no_host_port db
check 'nginx publica el puerto 80' nginx_port_80

if (( failures > 0 )); then
  printf 'FALLA: %d comprobación(es) fallaron.\n' "$failures" >&2
  exit 1
fi
printf 'OK: todas las comprobaciones pasaron.\n'
