# NordVPN Meshnet — Home Assistant Add-on

## Goal

A Home Assistant OS add-on that runs the NordVPN Linux client in **Meshnet mode**, creating a system-wide tunnel interface. Other Meshnet peers can then reach HA and any service on the host LAN.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Home Assistant OS (host)                             │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │  meshnet add-on (Docker, host_network)       │    │
│  │                                              │    │
│  │  nordvpnd ←─ token auth ─→ NordVPN cloud    │    │
│  │  nordvpn CLI                                │    │
│  │  meshnet0 (tunnel interface)                │    │
│  │  nginx (Web UI / healthcheck)               │    │
│  └──────────────────────────────────────────────┘    │
│       │                                              │
│       │  host_network: true → tunnel is host-wide   │
│       │                                              │
│  ┌─────────────┐   ┌──────────────┐                 │
│  │  HA Core    │   │  other add-ons│                 │
│  └─────────────┘   └──────────────┘                 │
│                                                      │
└──────────────────────────────────────────────────────┘
       │
       │  Meshnet peers (phones, laptops, remote servers)
       │  reach this host via its Nord name or Meshnet IP
       ▼
  peer-device.nord  →  100.x.x.x (Meshnet IP)
```

**Why `host_network: true`?** The Meshnet tunnel (`meshnet0`) is created inside the container's network namespace by default. With `host_network`, the container shares the host's network stack — the tunnel appears on the host, and HA / other add-ons are reachable from Meshnet peers.

---

## Repository Structure

```
nordvpn-meshnet-haos/
├── meshnet/
│   ├── Dockerfile
│   ├── config.yaml
│   ├── DOCS.md
│   ├── rootfs/
│   │   ├── etc/
│   │   │   └── s6-overlay/
│   │   │       └── services.d/
│   │   │           ├── nordvpnd/
│   │   │           │   └── run
│   │   │           ├── nordvpn-setup/
│   │   │           │   └── run
│   │   │           └── webui/
│   │   │               ├── run
│   │   │               └── nginx.conf
│   │   └── usr/
│   │       └── src/
│   │           ├── healthcheck
│   │           └── webui.sh
│   ├── translations/
│   │   └── en.yaml
│   ├── icon.png
│   └── logo.png
├── README.md
└── LICENSE
```

---

## Phase 1 — Add-on skeleton

### 1.1 Dockerfile
- **Base:** `ghcr.io/hassio-addons/debian-base:13.3.0` (Debian 13 "trixie" with s6-overlay v3)
  - NordVPN's `.deb` packages require Debian/Ubuntu. Alpine is not supported.
- Install NordVPN from official APT repo (`repo.nordvpn.com`)
- Install `nginx`, `curl`, `iproute2`, `iptables`
- Copy `rootfs/` to `/`
- Set s6-overlay as init, `init: false` in config.yaml
- Labels: `io.hass.type=addon`, `io.hass.arch`, `io.hass.version`

### 1.2 config.yaml
```yaml
name: "NordVPN Meshnet"
version: "1.0.0"
slug: "nordvpn_meshnet"
description: "Meshnet tunnel for remote Home Assistant access"
url: "https://github.com/<user>/nordvpn-meshnet-haos"
arch:
  - aarch64
  - amd64
startup: services          # start before HA core, after system services
boot: auto
init: false                # s6-overlay is PID 1
host_network: true         # tunnel is host-wide
privileged:
  - NET_ADMIN
  - NET_RAW
devices: []                # no TUN device needed for Meshnet
map:
  - addon_config:ro
timeout: 60
ingress: true              # Web UI via HA panel
ingress_port: 80
options:
  token: ""
  nickname: ""
  allow_routing: "*"
  allow_local_network: "*"
  allow_fileshare: "*"
  allow_remote: "*"
schema:
  token: "str?"
  nickname: "str?"
  allow_routing: "str?"
  allow_local_network: "str?"
  allow_fileshare: "str?"
  allow_remote: "str?"
```

**Key config decisions:**
- `startup: services` — Meshnet needs to be up before HA core starts so peers can reach it
- `host_network: true` — tunnel is visible host-wide (like the Tailscale add-on)
- `ingress: true` + `ingress_port: 80` — Web UI accessible from HA dashboard
- No `ports` mapping needed (host_network already exposes everything)

### 1.3 DOCS.md
Full user documentation: installation, token generation, configuration options, troubleshooting.

---

## Phase 2 — Startup logic (s6-overlay services)

### 2.1 `nordvpnd` service — daemon
- Starts `nordvpnd` (the NordVPN background daemon)
- Waits for it to be ready (polls `nordvpn status` until it responds)
- Must start first (other services depend on it)

### 2.2 `nordvpn-setup` service — one-time configuration
- Reads `/data/options.json` via `bashio`
- Authenticates: `nordvpn login --token "<token>"`
- Enables Meshnet: `nordvpn set meshnet on`
- Sets nickname (optional): `nordvpn nickname set "<name>"`
- Configures peer permissions:
  - `nordvpn meshnet peer allow routing <peers>`
  - `nordvpn meshnet peer allow local <peers>`
  - `nordvpn meshnet peer allow fileshare <peers>`
  - `nordvpn meshnet peer allow remote <peers>`
- `*` wildcard = allow for all peers
- Exits after setup (s6 runs it once on first boot; token persists in daemon state)

### 2.3 `webui` service — status dashboard
- Lightweight nginx serving a static HTML page
- Backend script (`webui.sh`) queried via nginx `proxy_pass` or `fastcgi`
- Shows: connection status, Nord name, Meshnet IP, peer list
- Healthcheck endpoint: `/health` returns 200 if Meshnet is connected

### 2.4 `healthcheck` script
- Called by Docker HEALTHCHECK
- Returns 0 if `nordvpn status` shows Meshnet connected
- Returns 1 otherwise

---

## Phase 3 — Meshnet peer permissions

The add-on config lets the user control what Meshnet peers can do:

| Permission | What it does | Default |
|---|---|---|
| `routing` | Peer can route internet traffic through this HA node | `*` (all) |
| `local_network` | Peer can reach LAN devices through this node | `*` (all) |
| `fileshare` | Peer can use NordVPN file sharing | `*` (all) |
| `remote` | Peer can access services on this node (SSH, HA Web UI) | `*` (all) |

Users can restrict to specific peer names: `peer-atlas.nord,peer-fuji.nord`

---

## Phase 4 — Web UI (Ingress)

Simple, informative dashboard accessible from HA's sidebar:

- **Connection status:** Connected / Disconnected / Error
- **Nord name:** e.g. `gkolotelo-altai.nord`
- **Meshnet IP:** e.g. `100.64.0.5`
- **Peers:** List of connected peers with status
- **Actions:** Reconnect, toggle Meshnet on/off
- **Logs:** Last 50 lines of nordvpnd output

Built with a minimal HTML/JS page + a shell script that parses `nordvpn status` / `nordvpn meshnet peer list` output and returns JSON.

---

## Phase 5 — Resilience

- **Token persistence:** `nordvpn logout --persist-token` on stop; re-auth on start
- **Hostname stability:** Container hostname set from add-on slug → Meshnet keeps the same Nord name across restarts
- **Auto-reconnect:** s6-overlay restarts `nordvpnd` if it crashes
- **IPv6:** NordVPN requires IPv6 for Meshnet. Ensure `net.ipv6.conf.all.disable_ipv6=0`

---

## Home Assistant compatibility

| Requirement | Detail |
|---|---|
| HA OS version | 2024.x+ (Supervisor with s6-overlay v3 base images) |
| Architectures | `aarch64` (Raspberry Pi), `amd64` (x86_64) |
| Prerequisites | NordVPN account with active subscription, Access Token |
| Network | `host_network` — peer devices must allow `remote` permission to reach HA |

---

## What this does NOT do

- ❌ Regular VPN tunneling (no `nordvpn connect` to NordVPN servers)
- ❌ Kill switch, Double VPN, Obfuscated servers
- ❌ qBittorrent proxy routing (Meshnet is the only mode)

---

## Verification checklist

- [ ] Add-on builds for both `aarch64` and `amd64`
- [ ] Add-on installs via HA add-store (custom repo)
- [ ] Token auth succeeds on first start
- [ ] Meshnet tunnel (`meshnet0`) appears on **host** network
- [ ] `ip addr show meshnet0` on host shows Meshnet IP
- [ ] Meshnet peers can `ping <meshnet-ip>`
- [ ] Meshnet peers can reach `http://<meshnet-ip>:8123` (HA Web UI)
- [ ] Web UI accessible via HA ingress panel
- [ ] Healthcheck passes when connected
- [ ] Add-on survives host reboot (token persists, Meshnet reconnects)
- [ ] Peer permissions configurable and applied correctly
