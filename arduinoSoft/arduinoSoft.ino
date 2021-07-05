#include <Wire.h>
#include "Pump.h"
#include "DosingQueue.h"
#define TdsSensorPin A2
#define PhSensorPin A3
#define VREF 5.0      // analog reference voltage(Volt) of the ADC
#define SCOUNT  30           // sum of sample point

int analogBuffer[SCOUNT];    // store the analog value in the array, read from ADC
int analogBufferTemp[SCOUNT];
int analogBufferIndex = 0,copyIndex = 0;
int averageVoltage = 0,tdsValue = 0,temperature = 25;

DosingQueue dosing_queue;
int pins1[4]={2,3,4,5};
SyringePump phPlusPump(pins1);
int pins2[4]={6,7,8,9};
SyringePump phMinusPump (pins2);
int pins3[4]={10,11,12,13};
SyringePump costamPump (pins3);
int sensor=0;
int pomp_buffer[2][30];

void receiveEvent(int byte_count) {
  if(Wire.read()==5){
    Serial.println("sensor change");
    sensor=(sensor+1)%2;
    return;
  }
  Wire.read(); //byte_count
  int pump = Wire.read();
  int dose = 1000*Wire.read();
  dosing_queue.add(pump,dose);
}
void requestEvent(){
  if(sensor==0){
    Serial.println("measuring tds");
    int tds=analogRead(TdsSensorPin);
    int compensationCoefficient=1.0+0.02*(temperature-25.0);    
    int compensationVolatge=tds/compensationCoefficient;  //temperature compensation
    tdsValue=(133.42*compensationVolatge*compensationVolatge*compensationVolatge - 255.86*compensationVolatge*compensationVolatge + 857.39*compensationVolatge)*0.5; //convert voltage value to tds value
    Wire.write(tdsValue);
  }
  else if(sensor==1){
    Serial.println("measuring ph");
    int ph=analogRead(PhSensorPin);
    int phValue=ph*5.0/1024/6*3.5;
    Wire.write(phValue);
  }
  else
    Wire.write(10);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Wire.begin(0x7);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
  pinMode(TdsSensorPin,INPUT);
}

void dosingActions(){
  while(!dosing_queue.is_empty()){
    int* dosing_action=dosing_queue.get_next();
    Serial.println(*dosing_action+" "+*(dosing_action+1));
    if(*dosing_action==1)
      phPlusPump.dosing(*(dosing_action+1));
    else if(*dosing_action==2)
      phMinusPump.dosing(*(dosing_action+1));
  }
  Serial.println("dosing queue empty");
}

void loop() {
  delay(500);
  dosingActions();
}
