import subprocess
import os
import threading
import time
import re
import sys

# Define the paths
script_path = r'C:\Users\David\Desktop\investing-news\investing-news.py'
log_file_path = r'C:\Users\David\Desktop\investing-news\output.log'
send_gradio_script = r'C:\Users\David\Desktop\investing-news\send_gradio_link.py'

def start_investing_news():
    with open(log_file_path, 'w') as log_file:
        process = subprocess.Popen(
            ['python', '-u', script_path],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )

    return process

def tail_log_file(stop_event):
    with open(log_file_path, 'r') as log_file:
        while not stop_event.is_set():
            line = log_file.readline()
            if line:
                print(line, end='')  # Print each line to stdout
            else:
                time.sleep(0.1)  # Sleep briefly and retry

def monitor_log_for_gradio_link(stop_event):
    gradio_url_pattern = re.compile(r'https://[a-zA-Z0-9.-]+\.gradio\.live(/[a-zA-Z0-9._/?&=-]*)?')

    while not stop_event.is_set():
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                match = gradio_url_pattern.search(line)
                if match:
                    url = match.group(0)
                    if len(url) > 12:
                        print(f"Gradio link found: {url}")
                        subprocess.run(['python', send_gradio_script, url])
                        stop_event.set()  # Signal to stop monitoring
                        return

        time.sleep(1)  # Check the file every second

def main():
    print("Loading...")

    process = start_investing_news()

    stop_event = threading.Event()

    # Start tailing the log file in a separate thread
    tail_thread = threading.Thread(target=tail_log_file, args=(stop_event,))
    tail_thread.start()

    # Start monitoring the log file for the Gradio link in a separate thread
    monitor_thread = threading.Thread(target=monitor_log_for_gradio_link, args=(stop_event,))
    monitor_thread.start()

    # Wait for both threads to finish
    tail_thread.join()
    monitor_thread.join()

if __name__ == "__main__":
    main()
