
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
        digitalWrite
      }
    }
  }
};
void setup() {
  // put your setup code here, to run once:
  int pins[4]={2,3,4,5};
  SyringePump phPlusPump(pins);

}

void loop() {
  // put your main code here, to run repeatedly:

}
