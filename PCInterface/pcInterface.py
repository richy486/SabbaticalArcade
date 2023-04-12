# Install these
# pywin32
# psutil
# PySerial


import serial 

import http.server
import socketserver
import threading
import configparser
from datetime import datetime
import json
import platform

# port = "/dev/tty.usbserial-1410"
# # port = "COM4"

print(f"ARCADE!!")

IGNORE_COIN_READER = True

config = configparser.ConfigParser()
config['ARDUINO'] = {'Port': 'COM4'}
config['COINREADER'] = {'Ignore': 0}

config.read('config.ini')

with open('config.ini', 'w') as configfile:
  config.write(configfile)


ARDUINO_PORT = config['ARDUINO']['Port']
IGNORE_COIN_READER = config['COINREADER']['ignore']

print(f"IGNORE_COIN_READER: {IGNORE_COIN_READER}")

# quit()

###### Setup ######

if IGNORE_COIN_READER == False:
  print(f"Trying Arduino on: {ARDUINO_PORT}")
  serialPort = serial.Serial(port = ARDUINO_PORT, 
                            baudrate=9600,
                            bytesize=8,
                            timeout=2,
                            stopbits=serial.STOPBITS_ONE)

serialString = ""                           # Used to hold data coming over UART

# Define the API handler
class MyAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Hello, World!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        response = b'You sent: ' + post_data
        self.wfile.write(response)

        # Send to Arduino via serial.
        if IGNORE_COIN_READER == False:
          stripped_string = post_data.decode().replace(" ", "").replace("\n", "").replace("\t", "")
          serialPort.write(stripped_string)


# Set up the server
PORT = 8000
handler = MyAPIHandler
httpd = socketserver.TCPServer(('', PORT), handler)

# Start the server on a separate thread
def start_server():
    print(f"Server running on port {PORT}")
    httpd.serve_forever()

server_thread = threading.Thread(target=start_server)
server_thread.start()


def activeApp():
  if platform.system() == 'Windows':
    # Import the win32gui library only if running on Windows
    import win32gui
    import win32process
    import psutil
    
    # Get the handle of the foreground window
    foreground_window = win32gui.GetForegroundWindow()

    # Get the process ID of the foreground window
    process_id = win32process.GetWindowThreadProcessId(foreground_window)[1]

    # Get the process information
    process = psutil.Process(process_id)

    # Get the executable name of the foreground process
    executable = process.name()

    # Print the information to the console
    return executable
  else:
    return "unknown"

print(f"Ready to loop")
###### Loop #######
while(1):

  # Wait until there is data waiting in the serial buffer
  if IGNORE_COIN_READER == False and (serialPort.in_waiting > 0):

    # Read data out of the buffer until a carraige return / new line is found
    serialString = serialPort.readline().decode('Ascii')
    print(serialString)

    # Parse the string into command:value elements
    command_value_pairs = serialString.split("&")
    input_json = {}
    for pair in command_value_pairs:
      command, value = pair.split(":")
      input_json[command] = value

    # Add the current date and time to the dictionary
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    input_json["date"] = date_string
    input_json["app"] = activeApp()

    json_string = json.dumps(input_json).replace('\\n', '').replace('\\r', '').replace('"', '')
    json_string += '\n'
    print(json_string)

    file = open("coinLog.txt", "a")

    file.write(json_string)
    file.close()

    # # Tell the device connected over the serial port that we recevied the data!
    # # The b at the beginning is used to indicate bytes!
    # serialPort.write(b"Thank you for sending data \r\n")