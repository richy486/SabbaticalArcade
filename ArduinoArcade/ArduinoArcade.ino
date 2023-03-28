/*
 * Arcade Coin Reader and Printer
 * Sends data and recieves data via serial in command:value(&) format
 * uses current time instead of a straight counter.
 */

/*  Install these
 *   Adafruit Thermal Printer library
 */

#include <EEPROM.h>
#include <Adafruit_Thermal.h>
#include <SoftwareSerial.h>

// ---- Coins -----
// Number of impulses detected
int impulseCount = 0;
int lastImpulseCount = 0;

// Sum of all the   coins inseted
float total_amount=0;
float coinValues[] = {2.0, 1.0, 0.5, 0.2, 0.1, 0.05};
int coinValueCount = sizeof(coinValues) / sizeof(float);

// Delta time.
const unsigned long eventInterval = 1000;
unsigned long lastImpulseTime = 0;

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

void setupCoins() {
  attachInterrupt(0,incomingImpuls, FALLING);
  EEPROM.get(0, total_amount);
  if (total_amount != total_amount) {
    total_amount = 0;
  }

  printTotal();
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

void loopCoins(unsigned long currentTime) {
  if (impulseCount != lastImpulseCount) {
     lastImpulseCount = impulseCount;
     lastImpulseTime = currentTime;
  }

  if (lastImpulseTime != 0 && currentTime - lastImpulseTime >= eventInterval) {
    if (impulseCount > 0 && impulseCount <= coinValueCount) {
      float coinValue = coinValues[impulseCount-1];
      total_amount = total_amount + coinValue;
      
      EEPROM.put(0, total_amount);
      Serial.print("coin:");Serial.print(coinValue);
      Serial.print("&total:"); Serial.println(total_amount);
    }
    impulseCount = 0;
    lastImpulseCount = 0;
    lastImpulseTime = 0;
  }
}

// --- Serial Input ---

void loopSerialInput(unsigned long currentTime) {
  // TODO: add new serial input.
}

// --- Coins ---

void incomingImpuls() {
  impulseCount = impulseCount + 1;
}

void printTotal() {
  Serial.print("total:"); Serial.println(total_amount);
}
