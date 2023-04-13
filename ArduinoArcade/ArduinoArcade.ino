/*
 * Arcade Coin Reader and Printer
 * Sends data and recieves data via serial in command:value(&) format
 * uses current time instead of a straight counter.
 */

/*  Install these
 *   Adafruit Thermal Printer library
 */

#include <Adafruit_Thermal.h>
#include <SoftwareSerial.h>
#include "coinReader.h"

// ----- Printer -----

#define TX_PIN 6 // Arduino TX pin -- RX on printer
#define RX_PIN 5 // Arduino RX pin -- TX on printer

SoftwareSerial printer_connection(RX_PIN, TX_PIN);
Adafruit_Thermal printer(&printer_connection);

void setup() {
  Serial.begin(9600);
  while (!Serial);
  
  setupCoins();
  setupPrinter();
}

void setupPrinter() {
  printer_connection.begin(19200);
  printer.begin();
}

void loop() {
  /* Updates frequently */
  unsigned long currentTime = millis();
  loopCoins(currentTime);
  loopSerialInput(currentTime);
}



// --- Serial Input ---

void loopSerialInput(unsigned long currentTime) {
  // TODO: add new serial input.
}
