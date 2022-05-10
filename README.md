# ADSBx to Event Hubs

Sends live ADSB aircraft location data to Azure Event Hubs.

## Setup

The easiest way to use this is to get started from the [ADSB Exchange Getting Started instructions](https://www.adsbexchange.com/how-to-feed/) using their [ADSBx Raspberry Pi image](https://www.adsbexchange.com/how-to-feed/). Once this is configured and running [you can verify this }y visiting their status page](https://www.adsbexchange.com/myip/) from the same outbound IP your sender is running on.

The ADSBx distribution runs an open TCP server on your network exposing a few variations of the data feed. This image uses port 30003 which supplies on line per event. This is paired with a simple Python program that pipes stdin into an Azure Event Hub, delimited by a line break. Then these are connected together by a simple pipe operation using a shell script.

### Python setup

Make sure python3 and pip3 and both installed. Once there in the project folder, run:

```bash
pip3 install -r requirements.txt
```

### Configuring Event Hub

Create an Azure Event Hub namespace and Azure Event Hub to receive the messages. In the Event Hub, open "Shared access policies" and create a new policy that has the "Send" claim. Once this is created, copy one of the connection strings (primary or secondary, either will work) and put that into the `.env` configuration file for the script. 

### Configuring the Sender Script

Extract this script into a folder on the Pi. (`/home/pi/adsb-eh-send` is a good choice.). Copy the supplied `example.env` file to `.env` and edit it, adding your Event Hub connection string and event hub name (see instructions above for getting this.)

### Running the Send Script Manually

To start sending, run the `start-send.sh` script. If everything is running correctly, this will start sending messages to the Event Hub. You can see the message stats in the Azure Portal on the Event Hub. The Requests, Messages and Throughput monitor counters should show activity on that Event Hub and namespace.

### Running the Send Script Automatically on Startup

TODO
