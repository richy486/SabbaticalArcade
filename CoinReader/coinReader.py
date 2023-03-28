# import pyfirmata
# import time

# board = pyfirmata.Arduino('/dev/tty.usbserial-1410')

# while True:
#     board.digital[13].write(1)
#     time.sleep(1)
#     board.digital[13].write(0)
#     time.sleep(1)


import serial

import http.server
import socketserver
import threading
import configparser

# port = "/dev/tty.usbserial-1410"
# # port = "COM4"

print(f"ARCADE!!")

config = configparser.ConfigParser()
config['ARDUINO'] = {'Port': 'COM4'}
config.read('config.ini')

with open('config.ini', 'w') as configfile:
  config.write(configfile)


arduinoPort = config['ARDUINO']['Port']
print(f"Trying Arduino on: {arduinoPort}")

# quit()

###### Setup ######



serialPort = serial.Serial(port = arduinoPort, 
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

print(f"Ready to loop")
###### Loop #######
while(1):

  # Wait until there is data waiting in the serial buffer
  if(serialPort.in_waiting > 0):

    # Read data out of the buffer until a carraige return / new line is found
    serialString = serialPort.readline().decode('Ascii')

    # Print the contents of the serial data
    print(serialString)

    file = open("coinLog.txt", "a")
    file.write(serialString)
    file.close()

    # # Tell the device connected over the serial port that we recevied the data!
    # # The b at the beginning is used to indicate bytes!
    # serialPort.write(b"Thank you for sending data \r\n")