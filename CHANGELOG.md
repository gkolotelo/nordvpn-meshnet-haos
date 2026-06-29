# Changelog

## v1.0.15 (2026-06-29)

- Disable NordVPN traffic routing on startup so Meshnet no longer needs to change host rp_filter/sysctl settings inside the add-on container.

## v1.0.14 (2026-06-29)

- Grant full add-on privileges needed by NordVPN to update `rp_filter` and install Meshnet routing rules.
- Use the NordVPN 5.x Meshnet nickname command (`nordvpn meshnet set nickname`) and fall back to the container hostname when no nickname is configured.

## v1.0.13 (2026-06-29)

- Avoid using `nordvpn status` for daemon readiness because it can trigger the analytics consent prompt.
- Pre-seed analytics consent as disabled before running authentication/status commands in the non-interactive add-on container.

## v1.0.12 (2026-06-29)

- Fix startup script syntax for reading token/nickname with `jq`.
- Install `ncat`, required by the status API server.
- Persist/provide machine IDs expected by NordVPN inside the HA add-on container.
- Stop stale `nordvpnd` processes before startup to avoid "daemon is already running" restart loops.

## v1.0.0 (2025-01-XX)

- Initial release
- NordVPN Meshnet mode (headless, token-based authentication)
- Configurable peer permissions (routing, local network, fileshare, remote)
- Web UI status dashboard (Nord name, Meshnet IP, peer list)
- Health checks for Docker and HA
- Debian base image (NordVPN .deb packages)
- s6-overlay process supervision
- `host_network: true` for system-wide tunnel visibility
