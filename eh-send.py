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

send_buffer=[]
oldest_buffer_date=None
max_buffer_size=50
max_buffer_age=5 #seconds
batch_count=0

def queue_event_data(payload):
    global send_buffer, oldest_buffer_date, max_buffer_size, max_buffer_age, batch_count
    event_data=EventData(payload)
    send_buffer.append(event_data)
    if oldest_buffer_date == None: 
        oldest_buffer_date = datetime.now()
    buffer_age=(datetime.now() - oldest_buffer_date).total_seconds()
    # Time to send?
    if (buffer_age > max_buffer_age) or (len(send_buffer) > max_buffer_size):
        send_event_data_batch(send_buffer)
        batch_count = batch_count + 1
        # reset the buffer
        send_buffer = []
        oldest_buffer_date=None


def send_event_data_batch(payloads):
    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.
    event_data_batch = producer.create_batch()
    for payload in payloads:
        event_data_batch.add(payload)
    producer.send_batch(event_data_batch)

stats_interval=30
msg_count = 0
start_time = datetime.now()
next_status_update = start_time
last_report_time = None

def report_status():
    global next_status_update, last_report_time
    cur_time = datetime.now()
    if next_status_update <= cur_time:
        report_time = (cur_time - last_report_time) if last_report_time is not None else None
        elapsed_time = cur_time - start_time
        elapsed_time_seconds = elapsed_time.total_seconds()
        avg_msg_sec_total = (msg_count / elapsed_time_seconds) if elapsed_time_seconds > 0 else 0
        avg_msg_sec_report = (msg_count / report_time.total_seconds()) if report_time is not None else 0
        print(f'send-eh: message count:{msg_count}, batches: {batch_count}, msg/sec cur:{avg_msg_sec_report:.1f}, msg/sec total: {avg_msg_sec_total:.1f}')
        sys.stdout.flush() 
        last_report_time = cur_time
        next_status_update = next_status_update + timedelta(seconds=stats_interval)

# Process incoming lines
for line in sys.stdin:
    report_status()
    line_stripped = line.replace('\n','')
    msg_count += 1
    queue_event_data(line_stripped)

