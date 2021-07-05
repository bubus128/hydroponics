#include "Arduino.h"
#include "Pump.h"

PerystalticPump::PerystalticPump(int pins[2]){
      for(int i=0;i<pinNum;i++){
        this->pins[i]=pins[i];
      }
  }
void PerystalticPump::dosing(int dose){
    //todo
}
SyringePump::SyringePump(int pins[4]){
  for(int i=0;i<this->pinNum;i++){
    this->pins[i]=pins[i];
  }
}
void SyringePump::dosing(int dose){
  while (dose>0){
    for(int i=0;i<this->pinNum;i++){
      digitalWrite(this->pins[i],HIGH);
      delay(this->stepDelay);
      digitalWrite(this->pins[i],LOW);
    }
    dose--;
  }
}
