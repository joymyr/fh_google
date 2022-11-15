# Somfy integration for Futurehome

This integration depends on cast-web-api https://github.com/vervallsweg/cast-web-api-cli
to integrate Google cast with futurehome.
Media devices will be automatically added to FH when running this integration.
The main purpose is to use it in automations to speak out messages,
but it also enables some controls from the FH-app.

## Requirements

* Cast-web-api-cli running locally
* Futurehome hub
* A local device where you can run this Pyhon code, i.e. a Raspberry PI

## Setup

* Enable local api in the Futurehome hub settings
* Install Python3 on a local device
```
# Example for Debian-based systems
sudo apt-get install python3 python3-pip
```

* Install this project and required dependencies
```bash
pip3 install requests paho-mqtt
git clone https://github.com/joymyr/fh-google.git
```

## Configuration

Edit const.py and set the required parameters

```
CAST_URL = "Url of your cast api client"
MQ_ADDRESS = "<Ip address of your Futurehome hub>"
MQ_USERNAME = "<Futurehome mq username>"
MQ_PASSWORD = "<Futurehome mq password>"
```

## Run

Run the code

```
python3 main.py
```

## Run on boot

Use systemctl to run the code on boot.
The fh_google.service file is intended for a Raspberry Pi.

```
sudo cp fh_google.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/fh_google.service
sudo systemctl daemon-reload
sudo systemctl enable fh_google.service
```
