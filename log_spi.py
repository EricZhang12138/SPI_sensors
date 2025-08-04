import serial
import datetime
import threading
import time
import csv

def print_to_console():
    global count
    while True:
        try:
            lock.acquire()
            print(buffer_data[:64].decode('utf-8',errors='ignore'))
            buffer_data.clear()
        finally:
            lock.release()
        time.sleep(5)

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600
counter =0
pattern = [b'\r',b'\n',b'\r',b'\n']
buffer_data = bytearray(64)
lock = threading.Lock()
buffer_str = ""


# create a unique filename based on the current date and time
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"data_log/spi_log_{timestamp}.csv"

print(f"Connecting to port {SERIAL_PORT} at {BAUD_RATE} bps...")



thread_print = threading.Thread(target = print_to_console,daemon=True)
thread_print.start()

try:
    with serial.Serial(SERIAL_PORT,BAUD_RATE,timeout=3) as ser:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.1)  # Give it a moment

        print(f"Connected. Logging data to '{log_filename}'. Press Ctrl+C to stop.")
        buffer_data.clear()
        # open the log file for writing
        with open(log_filename,'w',newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp','tmp126 reading','lm95071 reading'])
            while True:
                #read any available data from the serial port
                incoming_byte = ser.read()
                
                if incoming_byte == pattern[counter]:
                    counter +=1
                else:
                    counter =0
                
                if counter ==4:
                    current_instant = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                    timestamp_message = f"Time: ({current_instant})\n".encode('utf-8')
                    timestamp_str = f"{current_instant}"
                    try:
                        lock.acquire()
                        buffer_data.extend(timestamp_message)
                    finally:
                        lock.release()
                    counter =0
                    buffer_str = buffer_data[:64].decode('utf-8')
                    tmp126_read = buffer_str[8:13]
                    lm9521_read = buffer_str[25:30]
                    writer.writerow([timestamp_str,tmp126_read,lm9521_read])
                     
                if incoming_byte:
                    #write the raw byte directly to the file
                    #covert the windows \r\n to linux \n
                    if incoming_byte == b'\r':
                        continue
                    try:
                        lock.acquire()
                        buffer_data.extend(incoming_byte)
                    finally:
                        lock.release()

                else:
                    print("data unavailable")


except serial.SerialException as e:
    print(f"Error: could not open serial port '{SERIAL_PORT}'.")
    print(f"Details: {e}")
except KeyboardInterrupt:
    print("\nLogging stopped by user. File saved.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")



