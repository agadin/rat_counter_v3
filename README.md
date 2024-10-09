
```
source myenv/bin/activate
sudo nano /etc/systemd/system/myscript.service

sudo systemctl daemon-reload
sudo systemctl enable myscript.service

sudo systemctl start myscript.service

sudo systemctl status myscript.service

sudo journalctl -u myscript.service -f

```