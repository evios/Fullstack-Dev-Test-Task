# Ghost on Hetzner with Tailscale-only SSH

This deployment runs Ghost and MySQL in Docker Compose. Caddy serves the blog over HTTPS and obtains certificates automatically. SSH is restricted to the Tailscale network; the only public application ports are TCP 80 and 443.

## Requirements

- A Hetzner Cloud VPS running Ubuntu 24.04, with a public IPv4 address.
- A DNS `A` record for the blog hostname pointing to the VPS.
- A local machine with `tailscale`, `ssh`, and `tar`.
- A Tailscale account and an auth key for the VPS. Create a non-reusable, pre-approved key (tagged if your tailnet policy requires it). Do not use an ephemeral key for a persistent server.
- The SSH public key of the administrator running deployments.

## One-time host bootstrap

Copy or paste `bootstrap.sh` to the VPS through the Hetzner web console; do not use public SSH to bootstrap it. Run the script as root, supplying the one-time Tailscale key and administrator public key:

```bash
read -rsp 'Tailscale auth key: ' TAILSCALE_AUTH_KEY
echo
export TAILSCALE_AUTH_KEY
export ADMIN_SSH_PUBLIC_KEY='ssh-ed25519 AAAA... admin@laptop'
export TAILSCALE_HOSTNAME='ghost-blog'
bash bootstrap.sh
unset TAILSCALE_AUTH_KEY
```

The script installs Docker, Compose, OpenSSH, and Tailscale; configures key-only SSH; and enables UFW with inbound access limited to SSH on `tailscale0` plus public HTTP and HTTPS. It does not open port 22 publicly. For defense in depth, configure the Hetzner Cloud Firewall to allow inbound TCP 80 and 443 only; do not add an SSH rule. Tailscale admin policy must allow the administrator to SSH to this VPS over the tailnet.

Keep the Tailscale key private. It is passed to the Tailscale client during bootstrap; revoke it in the Tailscale admin console after enrollment if it remains listed.

## Deploy and update Ghost

Make sure the domain resolves to this server and that the deployment machine is connected to the same Tailscale network. Then run from the repository root:

```bash
DOMAIN=blog.example.com VPS_HOST=ghost-blog ./infra/ghost/deploy.sh
```

`VPS_HOST` is the VPS's Tailscale DNS name or Tailscale IP, not its public IP. The script refuses to continue unless it can reach the host over Tailscale and SSH.

On first use, connect once with `ssh root@ghost-blog` to verify and save the host key before running the non-interactive deployment script.

The first deployment creates a mode-600 `.env` on the VPS with random MySQL passwords. Later deployments preserve it and the named Docker volumes. Back up `/opt/ghost-blog/.env` and the `mysql-data`, `ghost-content`, `caddy-data`, and `caddy-config` volumes. To change domains, update `DOMAIN` in that `.env` deliberately and redeploy.

Ghost setup is available at `https://blog.example.com/ghost/`. Certificate issuance requires working DNS and public inbound access to ports 80 and 443. SSH is never required from the public internet.

## Operations

Connect to the VPS through Tailscale:

```bash
ssh root@ghost-blog
cd /opt/ghost-blog
docker compose --env-file .env ps
docker compose --env-file .env logs -f ghost
```

Update images and restart with the deployment command. Back up Ghost content and MySQL data before upgrading major versions.
