#include <Wire.h>
class Pump{
  int pinNum;
  int capacity;
  int level;
  virtual void dosing(int dose);
};
class PerystalticPump:Pump{
  static const int pinNum=2;
  int pins[pinNum];
  PerystalticPump(int pins[2]){
      for(int i=0;i<pinNum;i++){
        this->pins[i]=pins[i];
      }
  }
  void dosing(int dose){

  }
};
class SyringePump:Pump{
  static const int pinNum=4;
  const int stepDelay=3;
  int pins[pinNum];
  public:
  SyringePump(int pins[4]){
    for(int i=0;i<pinNum;i++){
      this->pins[i]=pins[i];
    }
  }
  void dosing(int dose){
    while (dose>0){
      for(int i=0;i<pinNum;i++){
        digitalWrite(this->pins[i],HIGH);
        delay(this->stepDelay);
        digitalWrite(this->pins[i],LOW);
      }
      dose--;
    }
  }
};

int pins1[4]={2,3,4,5};
SyringePump phPlusPump(pins1);
int pins2[4]={6,7,8,9};
SyringePump phMinusPump (pins2);
int pins3[4]={10,11,12,13};
SyringePump costamPump (pins3);

void receiveEvent(int byte_count) {
  for (int i = 0; i < byte_count; i++) {
    int data_to_echo = Wire.read();
  }
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
