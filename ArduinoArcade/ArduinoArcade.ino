/*
 * Arcade Coin Reader and Printer
 * Sends data and recieves data via serial in command:value(&) format
 * uses current time instead of a straight counter.
 */

/*  Install these
 *   Adafruit Thermal Printer library
 */

#include "coinReader.h"
#include "printer.h"

void setup() {
  Serial.begin(9600);
  while (!Serial);
  
  setupCoins();
  setupPrinter();
}

void loop() {
  /* Updates frequently */
  unsigned long currentTime = millis();
  loopCoins(currentTime);
  loopSerialInput(currentTime);
}
