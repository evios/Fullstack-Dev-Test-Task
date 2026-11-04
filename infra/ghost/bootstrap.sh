#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script as root from the Hetzner web console." >&2
  exit 1
fi

if [[ -z "${TAILSCALE_AUTH_KEY:-}" || -z "${ADMIN_SSH_PUBLIC_KEY:-}" ]]; then
  echo "Set TAILSCALE_AUTH_KEY and ADMIN_SSH_PUBLIC_KEY before running this script." >&2
  exit 1
fi

if [[ ! -f /etc/os-release ]] || ! grep -q '^ID=ubuntu$' /etc/os-release; then
  echo "This bootstrap supports Ubuntu only." >&2
  exit 1
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ca-certificates \
  curl \
  docker.io \
  docker-compose-v2 \
  openssl \
  openssh-server \
  ufw
systemctl enable --now docker
systemctl enable --now ssh

curl -fsSL https://tailscale.com/install.sh | sh
tailscale up --auth-key="${TAILSCALE_AUTH_KEY}" --hostname="${TAILSCALE_HOSTNAME:-ghost-blog}"
unset TAILSCALE_AUTH_KEY

install -d -m 700 /root/.ssh
touch /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
if ! grep -qxF -- "${ADMIN_SSH_PUBLIC_KEY}" /root/.ssh/authorized_keys; then
  printf '%s\n' "${ADMIN_SSH_PUBLIC_KEY}" >>/root/.ssh/authorized_keys
fi

cat >/etc/ssh/sshd_config.d/60-ghost-tailscale.conf <<'EOF'
PasswordAuthentication no
PermitRootLogin prohibit-password
EOF
sshd -t
systemctl reload ssh

ufw default deny incoming
ufw default allow outgoing
ufw allow in on tailscale0 to any port 22 proto tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "Bootstrap complete. SSH is permitted only over Tailscale; the blog ports are public."
tailscale ip -4
