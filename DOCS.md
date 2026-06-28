# NordVPN Meshnet — Home Assistant Add-on

## Overview

This add-on runs the official NordVPN Linux client in **Meshnet mode** inside a Home Assistant OS container. It creates a system-wide tunnel interface (`meshnet0`) that other Meshnet peers can use to reach your Home Assistant instance and services on your local network.

Unlike regular VPN, Meshnet creates a peer-to-peer encrypted network between your devices — no central exit node, no traffic routing through Nord's servers.

## Prerequisites

- **Home Assistant OS** (Supervised, Container, or core installations don't support add-ons)
- **Active NordVPN subscription** (Meshnet is included with all plans)
- **Access Token** — generated from your Nord Account dashboard:
  1. Log in to [my.nordaccount.com](https://my.nordaccount.com/)
  2. Go to **NordVPN** → **Advanced settings**
  3. Scroll to **Meshnet (by NordVPN)** → **View details**
  4. Scroll to **Manual setup** → **Setup NordVPN manually**
  5. Enter your email verification code
  6. Click **Generate new token** (choose Permanent, not Temporary)
  7. **Copy the token immediately** — it's shown only once

## Installation

1. In Home Assistant, go to **Settings** → **Add-ons**
2. Click **Add-on Store** → **Repositories** (three dots menu)
3. Add the repository URL: `https://github.com/gkolotelo/nordvpn-meshnet-haos`
4. Find **NordVPN Meshnet** and click **Install**
5. Configure the add-on (see below)
6. Click **Start**

## Configuration

### Required: Access Token

In the add-on options, paste your Access Token. This authenticates the NordVPN daemon to your account.

### Optional: Device Nickname

By default, your device gets a random Nord name (e.g., `gkolotelo-altai.nord`). Set a custom nickname to make it easier to identify:

```yaml
nickname: "home-assistant"
```

### Peer Permissions

Control what Meshnet peers can do through your device. Use `*` to allow all peers, or specify peer names:

```yaml
allow_routing: "peer-atlas.nord,peer-fuji.nord"
allow_local_network: "*"
allow_fileshare: "*"
allow_remote: "*"
```

| Permission | What it does | Default |
|---|---|---|
| `routing` | Peer can route internet traffic through this node | All peers |
| `local_network` | Peer can reach your LAN devices through this node | All peers |
| `fileshare` | Peer can use NordVPN file sharing with this node | All peers |
| `remote` | Peer can access services on this node (HA Web UI, SSH, etc.) | All peers |

### Full Example

```yaml
token: "your-access-token-here"
nickname: "home-assistant"
allow_routing: "*"
allow_local_network: "peer-phone.nord,peer-laptop.nord"
allow_fileshare: "*"
allow_remote: "*"
```

## Usage

### Finding Your Meshnet Details

After starting the add-on:
1. Open the add-on's **Web UI** from the sidebar
2. Your **Nord name** (e.g., `gkolotelo-home-assistant.nord`) is displayed
3. Your **Meshnet IP** (e.g., `100.64.0.5`) is displayed

Other Meshnet peers can now reach:
- **Home Assistant:** `http://<meshnet-ip>:8123`
- **Your LAN services:** `http://<meshnet-ip>:<port>` (if `local_network` permission is set)

### Adding This Device to Other Peers

On other devices with NordVPN installed:
1. Enable Meshnet (`nordvpn set meshnet on`)
2. Your HA device should appear in the peer list automatically (if it's your account)
3. Or send an invitation: `nordvpn meshnet invite <email>`

### Managing Peer Permissions

To change permissions without reinstalling:
1. Update the add-on options in HA
2. Restart the add-on (changes are applied on startup)

## Troubleshooting

### "Token expired" error
Generate a new token from your Nord Account. Old tokens expire when you run `nordvpn logout` (use `nordvpn logout --persist-token` instead).

### Meshnet not appearing in peer list
- Ensure the add-on is running (check logs)
- Verify your token is valid and hasn't expired
- Check that `meshnet0` interface exists: `ip addr show meshnet0`

### Peers can't reach HA
- Ensure `allow_remote` includes the peer name or `*`
- Ensure your firewall allows port 8123 (HA's default port)
- Check that the peer has the correct Meshnet IP

### Add-on won't start
- Verify you're on Home Assistant OS (not Core/Container)
- Check that `host_network: true` is supported on your setup
- Review the add-on logs for specific errors

## Credits

Based on the official [NordVPN Linux client](https://github.com/NordSecurity/nordvpn-linux).
