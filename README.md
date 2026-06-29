# NordVPN Meshnet

A Home Assistant OS add-on that runs the official NordVPN Linux client in **Meshnet mode**, creating a system-wide tunnel interface. Other Meshnet peers can then reach your Home Assistant instance and services on your local network.

## Features

- **Headless authentication** — Uses NordVPN's access token (no browser required)
- **Meshnet-only mode** — Creates a peer-to-peer encrypted network, not a traditional VPN tunnel
- **System-wide tunnel** — `host_network: true` makes the tunnel visible on the host, so HA and other add-ons are reachable from Meshnet peers
- **Configurable peer permissions** — Control what each peer can do (LAN access, file sharing, remote access)
- **Web UI** — Status dashboard accessible from the HA sidebar via ingress
- **Health checks** — Docker and HA monitor connection status

## Quick Start

1. Install the add-on from the HA Add-on Store (add the repository)
2. Generate an Access Token from your [Nord Account](https://my.nordaccount.com/) → NordVPN → Advanced settings → Meshnet → Manual setup
3. Paste the token into the add-on options
4. Start the add-on

Your HA instance is now reachable from any Meshnet peer by its Meshnet IP address.

## Documentation

Full documentation: [meshnet/DOCS.md](meshnet/DOCS.md)

## Repository Structure

```
nordvpn-meshnet-haos/
└── meshnet/
    ├── Dockerfile          # Builds the add-on image (Debian + NordVPN + nginx)
    ├── config.yaml         # Add-on configuration (slug, options, schema)
    ├── DOCS.md             # User documentation
    ├── rootfs/
    │   └── etc/s6-overlay/
    │       └── services.d/
    │           ├── nordvpnd/run          # NordVPN daemon (PID 1 process)
    │           ├── nordvpn-setup/run     # One-time: auth, Meshnet enable, peer config
    │           └── webui/run             # Status dashboard (nginx + bash API)
    └── translations/
        └── en.yaml           # English translations
```

## License

MIT
