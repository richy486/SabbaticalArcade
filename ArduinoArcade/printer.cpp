#include "printer.h"
#include <Arduino.h>
#include <Adafruit_Thermal.h>
#include <SoftwareSerial.h>

#define TX_PIN 6 // Arduino TX pin -- RX on printer
#define RX_PIN 5 // Arduino RX pin -- TX on printer

SoftwareSerial printer_connection(RX_PIN, TX_PIN);
Adafruit_Thermal printer(&printer_connection);

#define INPUT_SIZE 400 // 384 max image width

char *text = NULL;

int bitmapWidth = 0;
int bitmapHeight = 0;
uint8_t *bitmapData = NULL;
int bitmapPos = 0;

const char delimiters[] = ",";

void clear();
bool checkSerial();
void printBlank(int lines = 2);
void printText();
void printImage();

void setupPrinter() {
  printer_connection.begin(19200);
  printer.begin();
  clear();
}

void loopSerialInput(unsigned long currentTime) {
  if (checkSerial()) {
    Serial.println("## end line input");

    if (text != NULL) {
      Serial.print("## text " );
      Serial.println(text);
      printText();
      Serial.println("## === end of text===");
      clear();
    }

    if (bitmapWidth != 0 && bitmapHeight != 0) {
      Serial.print("## width " );
      Serial.print(bitmapWidth);            
      Serial.print(" height " );
      Serial.println(bitmapHeight);
      
      Serial.print("## bitmapPos ");
      Serial.print(bitmapPos);
      Serial.println(" ");
      if (bitmapPos >= (bitmapWidth * bitmapHeight) / 8) {
        printImage();
        Serial.println("## === end of bitmap ===");
        clear();
      }
    }
  }
}

// Return true for found input/
bool checkSerial() {
  if(!Serial.available()) {
    return false;
  }

  // Get next command from Serial (add 1 for final 0)
  char input[INPUT_SIZE + 1];
  byte size = Serial.readBytes(input, INPUT_SIZE);
  // Add the final 0 to end the C string
  input[size] = 0;

  // Read each command pair 
  char* command = strtok(input, "&");
  while (command != 0) {
    // Split the command in two values
    char* value = strchr(command, ':');
    if (value != 0) {
      // Actually split the string in 2: replace ':' with 0
      *value = 0;
      ++value;

      Serial.print("## command " );
      Serial.print(command);
      Serial.print(" value " );
      Serial.println(value);

      if (strcmp(command, "clear") == 0) {
        clear();
      }
      if (strcmp(command, "feed") == 0) {
        printBlank();
      }

      if (strcmp(command, "text") == 0) {
        text = (char*)malloc(strlen(value));
        strcpy(text, value);
      }

      if (strcmp(command, "bitmapWidth") == 0) {
        bitmapWidth = atoi(value);
      }
      if (strcmp(command, "bitmapHeight") == 0) {
        bitmapHeight = atoi(value);
      }
      if (strcmp(command, "bitmapData") == 0) {

        if (bitmapHeight == 0 || bitmapWidth == 0) {
          Serial.print("## Error, width and height can't be zero before receiving bitmap data. width " );
          Serial.print(bitmapWidth);            
          Serial.print(" height " );
          Serial.println(bitmapHeight);
          return false;
        }
        if (bitmapWidth % 8 != 0 || bitmapHeight % 8 != 0) {          
          Serial.print("## Error, width and height must be a multiple of 8. width " );
          Serial.print(bitmapWidth);            
          Serial.print(" height " );
          Serial.println(bitmapHeight);
        }
        if (bitmapData == NULL) {
          bitmapData = (uint8_t*)malloc((bitmapWidth * bitmapHeight) / 8);
        }

        char *ptr;
        int inputIndex = 0;
      
        ptr = strtok(value, delimiters);
        while (ptr != NULL) {
          bitmapData[bitmapPos] = (uint8_t) strtol(ptr, 0, 16);
          bitmapPos++;
          inputIndex++;
          ptr = strtok(NULL, delimiters);
          
        }
      }
    }
    // Find the next command in input string
    command = strtok(0, "&");

    if (command == 0) {
      return true;
    }
  }
  return false;
}

void clear() {
  free(text);
  text = NULL;
  
  bitmapWidth = 0;
  bitmapHeight = 0;
  free(bitmapData);
  bitmapData = NULL;
  bitmapPos = 0;

  Serial.print("## hasPaper " ); Serial.println(printer.hasPaper());
  Serial.println("## -= Clear =-");
  
}

//// ---- Print -----

void printBlank(int lines) {
  printer.feed(lines);
}

void printText() {
  if (text == NULL) {
    Serial.println("## No text to print");
  }

  printer.wake();       // MUST wake() before printing again, even if reset
  printer.setDefault(); // Restore printer to defaults
  
  printer.println(text);
  printer.println();
}

void printImage() {
  if (bitmapWidth == 0 || bitmapHeight == 0 || bitmapData == NULL) {
    Serial.println("## Incorrect data for image print");
  }

  printer.wake();       // MUST wake() before printing again, even if reset
  printer.setDefault(); // Restore printer to defaults

  printer.printBitmap(bitmapWidth, bitmapHeight, bitmapData, false);
  printer.println();
}
