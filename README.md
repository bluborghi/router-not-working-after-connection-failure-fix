```bash
sudo nano /etc/systemd/system/internet-checker.service
```
```bash
[Unit]
Description=Servizio di controllo connessione internet

[Service]
ExecStart=/usr/bin/python3 /home/blubo/internet_checker/connection-check.py
Restart=always
User=blubo
WorkingDirectory=/home/blubo/internet_checker
Environment=PATH=/usr/bin:/usr/local/bin
Environment=PYTHONUNBUFFERED=1
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable internet-checker.service
sudo systemctl start internet-checker.service
sudo systemctl status internet-checker.service
```
