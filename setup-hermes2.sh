#!/bin/bash
set -e

# --- Configuration ---
HERMES_DIR="/home/justin/.hermes/hermes-agent"
VENV="$HERMES_DIR/venv"
PY="$VENV/bin/python3"
PIP="$VENV/bin/pip"

echo "🚀 Starting Full Hermes Mesh Transformation (Trinity Edition)..."
cd "$HERMES_DIR"

# 1. System & Venv Dependencies
echo "📦 Installing system dependencies..."
sudo apt-get update -y && sudo apt-get install -y python3-psutil curl

echo "📦 Upgrading virtual environment dependencies..."
$PIP install psutil fire starlette uvicorn agent-client-protocol || echo "⚠️ Some pip installs failed, proceeding anyway..."

# 2. Tailscale Mesh Setup
if ! command -v tailscale &> /dev/null; then
    echo "📡 Installing Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
fi
echo "📡 Refreshing Mesh Networking..."
sudo tailscale up --accept-routes --ssh || true

# 3. Create Systemd Services
mkdir -p ~/.config/systemd/user

# --- SERVICE 1: MCP Tool Server (Port 8642) ---
cat > ~/.config/systemd/user/hermes-mcp.service << EOF
[Unit]
Description=Hermes MCP Tool Server
After=network.target

[Service]
Type=simple
WorkingDirectory=$HERMES_DIR
ExecStart=$PY $HERMES_DIR/mcp_serve.py --port 8642 --host 0.0.0.0
Restart=always
RestartSec=5
Environment=PATH=$VENV/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=default.target
EOF

# --- SERVICE 2: ACP Agent Mesh (Port 8643) ---
cat > ~/.config/systemd/user/hermes-acp.service << EOF
[Unit]
Description=Hermes ACP Agent Mesh
After=network.target

[Service]
Type=simple
WorkingDirectory=$HERMES_DIR
ExecStart=$PY $HERMES_DIR/acp_serve.py --port 8643 --host 0.0.0.0
Restart=always
RestartSec=5
Environment=PATH=$VENV/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=default.target
EOF

# --- SERVICE 3: Messaging Gateway (The Brain) ---
cat > ~/.config/systemd/user/hermes-gateway.service << EOF
[Unit]
Description=Hermes Messaging Gateway
After=network.target hermes-mcp.service hermes-acp.service

[Service]
Type=simple
WorkingDirectory=$HERMES_DIR
ExecStart=$PY -m hermes_cli.main gateway run --replace
Restart=always
RestartSec=10
Environment=PATH=$VENV/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
# Ensure logs are captured correctly
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

# 4. Finalize and Start
echo "🔄 Reloading Cluster Control Plane..."
systemctl --user daemon-reload
systemctl --user enable hermes-mcp.service hermes-acp.service hermes-gateway.service
echo "⚡ Starting the Trinity Mesh (MCP + ACP + Gateway)..."
systemctl --user restart hermes-mcp.service hermes-acp.service hermes-gateway.service

echo "✅ Hermes Full Mesh Transformation Complete!"
echo "------------------------------------------------"
echo "Tailscale IP: $(tailscale ip -4)"
echo "MCP (Tools):   Port 8642"
echo "ACP (Agents):  Port 8643"
echo "Gateway:      Active (Integrated)"
echo "------------------------------------------------"
echo "Monitor the entire mesh with:"
echo "watch -n 2 'systemctl --user status hermes-mcp hermes-acp hermes-gateway'"