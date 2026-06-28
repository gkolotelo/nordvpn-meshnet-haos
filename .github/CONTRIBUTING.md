# Meshnet Status Add-on

This add-on runs the official NordVPN Linux client in Meshnet mode, creating a system-wide tunnel interface for remote Home Assistant access.

## Features

- Headless authentication via access token
- Meshnet-only mode (peer-to-peer encrypted network)
- System-wide tunnel visibility (`host_network: true`)
- Configurable peer permissions
- Web UI status dashboard
- Health checks

## Installation

1. Add the repository to your HA Add-on Store
2. Install the "NordVPN Meshnet" add-on
3. Configure your access token
4. Start the add-on

## Documentation

Full documentation available in [meshnet/DOCS.md](meshnet/DOCS.md).

## Repository Structure

```
nordvpn_hacs/
└── meshnet/
    ├── Dockerfile
    ├── config.yaml
    ├── DOCS.md
    ├── rootfs/
    │   └── etc/s6-overlay/
    │       └── services.d/
    │           ├── nordvpnd/run
    │           ├── nordvpn-setup/run
    │           └── webui/run
    └── translations/
        └── en.yaml
```

## License

MIT
