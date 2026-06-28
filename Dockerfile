FROM ghcr.io/hassio-addons/debian-base:9.3.0

ARG BUILD_ARCH
ARG BUILD_VERSION

# Install NordVPN and dependencies
RUN \
  apt-get update && \
  apt-get install -y --no-install-recommends \
    curl \
    wget \
    apt-transport-https \
    ca-certificates \
    jq \
    iproute2 \
    iptables \
    nginx \
    procps && \
  curl -sL "https://repo.nordvpn.com/gpg/nordvpn_public.asc" | \
    gpg --dearmor -o /usr/share/keyrings/nordvpn.gpg && \
  echo "deb [signed-by=/usr/share/keyrings/nordvpn.gpg] https://repo.nordvpn.com/deb/nordvpn/debian stable main" > \
    /etc/apt/sources.list.d/nordvpn.list && \
  apt-get update && \
  apt-get install -y --no-install-recommends nordvpn && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Copy rootfs overlay
COPY rootfs/ /

LABEL \
  io.hass.name="NordVPN Meshnet" \
  io.hass.description="Meshnet tunnel for remote Home Assistant access" \
  io.hass.arch="${BUILD_ARCH}" \
  io.hass.type="addon" \
  io.hass.version=${BUILD_VERSION} \
  maintainer="gkolotelo" \
  org.opencontainers.image.title="NordVPN Meshnet" \
  org.opencontainers.image.description="Meshnet tunnel for remote Home Assistant access" \
  org.opencontainers.image.vendor="gkolotelo" \
  org.opencontainers.image.licenses="MIT"
