# Cloudflare Tunnel Setup Guide

This guide shows how to expose your Streamlit app using Cloudflare Tunnel.

## Prerequisites

- Cloudflare account (free tier works)
- Cloudflared installed on your machine
- Your Streamlit app running locally

## Quick Start

### 1. Install Cloudflared

**Windows:**
```powershell
# Download from: https://github.com/cloudflare/cloudflared/releases
# Or use Chocolatey:
choco install cloudflared

# Or use Scoop:
scoop install cloudflared
```

**Mac:**
```bash
brew install cloudflared
```

**Linux:**
```bash
# Download from releases page or use package manager
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

### 2. Authenticate Cloudflared

```bash
cloudflared tunnel login
```

This will open a browser window to authenticate with Cloudflare.

### 3. Create a Named Tunnel (Optional but Recommended)

```bash
# Create tunnel
cloudflared tunnel create ai-smart-advisor

# This will output a tunnel UUID - save it!
```

### 4. Configure Tunnel

Create `config.yml` in your project root:

```yaml
tunnel: <your-tunnel-id>
credentials-file: /path/to/credentials.json

ingress:
  - hostname: ai-smart-advisor.yourdomain.com
    service: http://localhost:8501
  - service: http_status:404
```

### 5. Run Your Streamlit App

In one terminal:
```bash
streamlit run src/frontend/app.py --server.port 8501
```

### 6. Start Cloudflare Tunnel

**Quick method (temporary URL):**
```bash
cloudflared tunnel --url http://localhost:8501
```

**Named tunnel method (permanent URL):**
```bash
cloudflared tunnel run ai-smart-advisor
```

### 7. Access Your App

- Quick method: Use the URL provided by Cloudflared
- Named tunnel: Access via your configured hostname

## DNS Configuration (For Named Tunnel)

1. Go to Cloudflare Dashboard → Zero Trust → Tunnels
2. Select your tunnel
3. Click "Configure" → "Public Hostname"
4. Add your subdomain (e.g., `ai-smart-advisor.yourdomain.com`)
5. Point it to your tunnel

## Running as a Service

### Windows (Service)

```powershell
# Install as service
cloudflared service install

# Start service
cloudflared service start
```

### Linux (Systemd)

Create `/etc/systemd/system/cloudflared.service`:

```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=your-user
ExecStart=/usr/local/bin/cloudflared tunnel run ai-smart-advisor
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

## Security Notes

- Cloudflare Tunnel provides encryption automatically
- No need to expose ports on your firewall
- Traffic is encrypted end-to-end
- Free tier includes unlimited bandwidth

## Troubleshooting

**Tunnel won't connect:**
- Check if Streamlit is running on port 8501
- Verify tunnel credentials
- Check Cloudflare dashboard for tunnel status

**Can't access via hostname:**
- Verify DNS configuration
- Check tunnel routing rules
- Ensure DNS propagation completed

## Benefits of Cloudflare Tunnel

✅ Free to use
✅ Automatic HTTPS/SSL
✅ No port forwarding needed
✅ Works behind firewalls/NAT
✅ DDoS protection included
✅ Analytics available
