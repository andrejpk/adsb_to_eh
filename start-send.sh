#!/bin/bash

# load config into env variables
source .env

# start the flow of events
nc localhost 30003 | ./eh-send.py $EVENT_HUB_CONNECTION_STRING $EVENT_HUB_NAME
