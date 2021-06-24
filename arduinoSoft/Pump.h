#ifndef Morse_h
#define Morse_h
#include "Arduino.h"
class Pump{
  int pinNum;
  int capacity;
  int level;
  virtual void dosing(int dose);
};
class PerystalticPump:Pump{
  private:
  static const int pinNum=2;
  int pins[pinNum];
  public:
  PerystalticPump(int pins[2]);
  void dosing(int dose);
};
class SyringePump:Pump{
  private:
  static const int pinNum=4;
  const int stepDelay=3;
  int pins[pinNum];
  public:
  SyringePump(int pins[4]);
  void dosing(int dose);
};
#endif
