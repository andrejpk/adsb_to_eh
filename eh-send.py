#!/bin/python3

import sys
from datetime import datetime, timedelta
from azure.eventhub import EventHubProducerClient, EventData
from azure.eventhub.exceptions import EventHubError

def show_usage():
    print("eh-send.py: Sends lines from stdin to Azure Event Hubs")
    print()
    print("Usage:")
    print("  ./eh-send.py EVENT_HUB_CONNECTION_STRING EVENT_HUB_NAME")
    print()
    
if len(sys.argv) < 3:
    show_usage()
    exit()

EVENT_HUB_CONNECTION_STRING= sys.argv[1]
EVENTHUB_NAME = sys.argv[2] 


print(f'Sending to event hub {EVENTHUB_NAME}')

producer = EventHubProducerClient.from_connection_string(
    conn_str=EVENT_HUB_CONNECTION_STRING,
    eventhub_name=EVENTHUB_NAME
)

def send_event_data_batch(payload):
    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.
    event_data_batch = producer.create_batch()
    event_data_batch.add(EventData(payload))
    producer.send_batch(event_data_batch)

stats_interval=60
msg_count = 0
start_time = datetime.now()
next_status_update = start_time

def report_status():
    global next_status_update
    cur_time = datetime.now()
    elapsed_time = cur_time - start_time
    elapsed_time_seconds = elapsed_time.total_seconds()
    avg_msg_sec_total = (msg_count / elapsed_time_seconds) if elapsed_time_seconds > 0 else 0
    if next_status_update <= cur_time:
        next_status_update = next_status_update + timedelta(seconds=stats_interval)
        print(f'send-eh: message count:{msg_count}, msg/sec: {avg_msg_sec_total:.1f}')

# Process incoming lines
for line in sys.stdin:
    report_status()
    line_stripped = line.replace('\n','')
    msg_count += 1
    send_event_data_batch(line_stripped)
