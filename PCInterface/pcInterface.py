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
import time

import base64
from PIL import Image
import io

# port = "/dev/tty.usbserial-1410"
# # port = "COM4"

print(f"ARCADE!!")

config = configparser.ConfigParser()
config['ARDUINO'] = {'port': 'COM4'}
config['ARDUINO'] = {'ignore': 0}

config.read('config.ini')

with open('config.ini', 'w') as configfile:
  config.write(configfile)


ARDUINO_PORT = config['ARDUINO']['port']

IGNORE_ARDUINO_SERIAL = 0
# IGNORE_ARDUINO_SERIAL = config['ARDUINO']['ignore'] == "1" ? 1 : 0
if config['ARDUINO']['ignore'] == "1":
  IGNORE_ARDUINO_SERIAL = 1

print(f"IGNORE_ARDUINO_SERIAL: {IGNORE_ARDUINO_SERIAL} ")
print(type(IGNORE_ARDUINO_SERIAL))

if IGNORE_ARDUINO_SERIAL == 0:
  print("NOT ignoring")
else:
  print("ignoring")

# quit()

###### Setup ######

if IGNORE_ARDUINO_SERIAL == 0:
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

    # Decode JSON
    python_object = json.loads(post_data.decode())
    # print(python_object)

    if "print" in python_object and isinstance(python_object["print"], list):
      for item in python_object["print"]:
        print(item)

        ## TEXT ##
        if "text" in item and isinstance(item["text"], str):
          
          textString = "text:" + item["text"]
          print(f"Sending to arduino: {textString}")
          encoded_string = textString.encode()
          serialPort.write(encoded_string)
          time.sleep(3)

        ## IMAGE ##
        if "image" in item and isinstance(item["image"], str):
          # convert base64 image to byte array
          #    

          base64_str = item["image"]
          print("base64_str:", base64_str)

          byteArrayString, size = convert_image_to_1bpp(base64_str)
          print("Byte array:", byteArrayString)
          print("Size:", size)

          if len(size) != 2:
            print("Error: No size info")
            continue

          arduinoSizeString = "bitmapWidth:" + str(size[0]) + "&bitmapHeight:" + str(size[1])
          print(f"Sending to arduino: {arduinoSizeString}")
          encoded_arduinoSizeString = arduinoSizeString.encode()
          serialPort.write(encoded_arduinoSizeString)
          time.sleep(3)

          split_strings = [byteArrayString[i:i+94] for i in range(0, len(byteArrayString), 96)]
          print(split_strings)

          print("split " + str(len(split_strings)) +  ": ")
          for byteArrayLine in split_strings:
            arduinoByteArrayLine = "bitmapData:" + byteArrayLine
            print(f"Sending to arduino: {arduinoByteArrayLine}")
            encoded_arduinoByteArrayLine = arduinoByteArrayLine.encode()
            serialPort.write(encoded_arduinoByteArrayLine)
            time.sleep(3)
        
        ## FEED ##
        if "feed" in item:
          print(f"Sending FEED arduino")
          encoded_arduinoFeed = "feed:".encode()
          serialPort.write(encoded_arduinoFeed)
          time.sleep(3)
  


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

def convert_image_to_1bpp(base64_str):
  # Decode the base64 string to bytes
  data = base64.b64decode(base64_str)

  # # Load the image from bytes
  # img = Image.frombytes("L", (int(len(data)*8**0.5), int(len(data)*8**0.5)), data)
  # Load image as PIL Image object
  img = Image.open(io.BytesIO(data))

  # Convert the image to 1 bit per pixel
  img_bw = img.convert("1")

  # Get the image data as a byte array
  byte_array = img_bw.tobytes()

  # Get the image size
  size = img_bw.size


  formattedString = ", ".join("0x{:02X}".format(b) for b in byte_array)

  return formattedString, size

print(f"Ready to loop")
###### Loop #######
while(1):

  # Wait until there is data waiting in the serial buffer
  if IGNORE_ARDUINO_SERIAL == 0 and (serialPort.in_waiting > 0):

    # Read data out of the buffer until a carraige return / new line is found
    serialString = serialPort.readline().decode('Ascii')
    print(serialString)

    output_json = {}

    # Parse the string into command:value elements
    command_value_pairs = serialString.split("&")
    # for pair in command_value_pairs:
    #   command, value = pair.split(":")
    #   output_json[command] = value


    for pair in command_value_pairs:
      # command, value = pair.split(":")
      command_value = pair.split(":", 1)
      if len(command_value) != 2:
        print("Error: separator not found in string " + pair)
        continue
      command, value = command_value
      output_json[command] = value


    # print("command_value_pairs:")
    # for item in command_value_pairs:
    #   print(item)


    







    # Add the current date and time to the dictionary
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    output_json["date"] = date_string
    output_json["app"] = activeApp()

    json_string = json.dumps(output_json).replace('\\n', '').replace('\\r', '').replace('"', '')
    json_string += '\n'
    print(json_string)

    file = open("coinLog.txt", "a")

    file.write(json_string)
    file.close()

    # # Tell the device connected over the serial port that we recevied the data!
    # # The b at the beginning is used to indicate bytes!
    # serialPort.write(b"Thank you for sending data \r\n")