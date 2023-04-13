#include "coinReader.h"
#include <Arduino.h>
#include <EEPROM.h>
#include <SoftwareSerial.h>

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

static void incomingImpuls();
void printTotal();

void setupCoins() {
  attachInterrupt(0, incomingImpuls, FALLING); // 
  EEPROM.get(0, total_amount);
  if (total_amount != total_amount) {
    total_amount = 0;
  }

  printTotal();
}

static void incomingImpuls() {
  impulseCount = impulseCount + 1;
}

void printTotal() {
  Serial.print("total:"); 
  Serial.println(total_amount);
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
