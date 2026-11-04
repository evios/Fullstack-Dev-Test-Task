#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  echo "Usage: DOMAIN=blog.example.com VPS_HOST=ghost-blog $0" >&2
}

if [[ -z "${DOMAIN:-}" || -z "${VPS_HOST:-}" ]]; then
  usage
  exit 2
fi

if [[ ${#DOMAIN} -gt 253 || ! "${DOMAIN}" =~ ^([A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$ ]]; then
  echo "DOMAIN must be a fully qualified hostname without a scheme, path, or port." >&2
  exit 2
fi

if [[ ! "${VPS_HOST}" =~ ^[A-Za-z0-9][A-Za-z0-9.-]*$ ]]; then
  echo "VPS_HOST must be a Tailscale DNS name or IP address." >&2
  exit 2
fi

for command in ssh tar tailscale; do
  if ! command -v "${command}" >/dev/null 2>&1; then
    echo "Required command not found: ${command}" >&2
    exit 1
  fi
done

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TARGET="root@${VPS_HOST}"
REMOTE_DIR="/opt/ghost-blog"

if ! tailscale ping --timeout=5s "${VPS_HOST}" >/dev/null; then
  echo "Cannot reach ${VPS_HOST} over Tailscale. Check that both devices are connected." >&2
  exit 1
fi

ssh -o BatchMode=yes "${TARGET}" true
ssh -o BatchMode=yes "${TARGET}" "install -d -m 750 '${REMOTE_DIR}'"

tar -C "${SCRIPT_DIR}" -czf - compose.yml Caddyfile |
  ssh -o BatchMode=yes "${TARGET}" "tar -xzf - -C '${REMOTE_DIR}'"

ssh -o BatchMode=yes "${TARGET}" bash -s -- "${DOMAIN}" "${REMOTE_DIR}" <<'REMOTE'
set -Eeuo pipefail
domain="$1"
remote_dir="$2"
cd "${remote_dir}"

if [[ ! -f .env ]]; then
  umask 077
  printf 'DOMAIN=%s\nMYSQL_ROOT_PASSWORD=%s\nMYSQL_PASSWORD=%s\n' \
    "${domain}" \
    "$(openssl rand -hex 32)" \
    "$(openssl rand -hex 32)" >.env
elif ! grep -qxF "DOMAIN=${domain}" .env; then
  echo "Existing .env uses a different domain. Update it deliberately before redeploying." >&2
  exit 1
fi

docker compose --env-file .env pull
docker compose --env-file .env up -d --remove-orphans
docker compose --env-file .env ps
REMOTE

echo "Deployment complete: https://${DOMAIN}"
