# wordclock
A simple python wordclock with a 12x12 (columns x rows), german [layout](layout.png).
Kudos to WTRipper

## Hardware I am using:  
- Raspberry Pi Zero
- 139 WS2812b Led stripes (120 LEDs/m) - I removed some LEDs due to my frame setting

## Setup

1. Install RPi WS281x module:
```
sudo pip install rpi_ws281x
```
2. Clone this repo:
```
git clone https://github.com/AJOCHAM/wordclock
```
3. Update Config (TODO)
4. Test:
```
python wordclock.py
```
5. Customize paths in [service file](wordclock.service):
```
WorkingDirectory=/home/pi/wordclock
ExecStart=/home/pi/wordclock/venv/bin/python wordclock.py
```
6. Move service file:
```
sudo mv wordclclock.service /etc/systemd/system/wordclock.service
```
7. Register service:
```
sudo systemctl daemon-reload
sudo systemctl enable wordclock
```
8. Restart your system:
```
sudo reboot now
```
Or start the service manually:
```
sudo systemctl start wordclock
```

## Logging
Systemd logs using journal. View the logs of the wordclock service:
```
journalctl -u microblog
```
The wordclock project itself creates a `wordclock.log` file in its working directory.

## License
The wordclock project is licensed under the terms of the [MIT License](LICENSE.md).

However, it includes third-party Open-Source libraries, 
which are licensed under their own respective Open-Source licenses.
See [3rd-party-licenses](3rd-party-licenses.md) for more info.

