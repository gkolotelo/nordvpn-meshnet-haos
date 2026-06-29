# Changelog

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
