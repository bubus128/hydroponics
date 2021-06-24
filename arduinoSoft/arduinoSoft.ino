#include <Wire.h>
#include "Pump.h"

int pins1[4]={2,3,4,5};
SyringePump phPlusPump(pins1);
int pins2[4]={6,7,8,9};
SyringePump phMinusPump (pins2);
int pins3[4]={10,11,12,13};
SyringePump costamPump (pins3);

void receiveEvent(int byte_count) {
  byte pump_num = Wire.read();
  phPlusPump.dosing(1000);
}

void requestEvent(){
  Wire.write(10);
}

void setup() {
  // put your setup code here, to run once:
  //Serial.begin(9600);
  Wire.begin(0x8);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
}

void loop() {

}
