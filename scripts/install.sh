#!/bin/bash

set -e

echo "[INFO] Python version:"
python3 --version

if [ ! -d ".venv" ]; then
  echo "[INFO] Creating virtual environment .venv..."
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "[INFO] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[INFO] Initializing app data..."
python -m velayne.scripts.init

cat <<EOF

[INFO] To run Velayne as a systemd service:

1. Create file /etc/systemd/system/velayne.service with contents:

-------------------------------------
[Unit]
Description=Velayne unified service
After=network.target

[Service]
Type=simple
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/.venv/bin/python -m velayne.run
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
-------------------------------------

2. Reload systemd daemon:
   sudo systemctl daemon-reload

3. Enable and start service:
   sudo systemctl enable velayne.service
   sudo systemctl start velayne.service

4. Check logs:
   journalctl -u velayne.service -f

EOF