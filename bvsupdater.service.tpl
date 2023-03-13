[Unit]
Description=Updater for BVS
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=%PWD%
ExecStart=%PWD%/main.py -d
Restart=on-failure

[Install]
WantedBy=multi-user.target
